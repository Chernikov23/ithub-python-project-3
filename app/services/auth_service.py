from sqlite3 import Cursor

from app import schema
from app.security import create_access_token, get_password_hash, verify_password


def register(*, cursor: Cursor, user_data: schema.UserCreate) -> None:
    password_hash = get_password_hash(user_data.password)

    cursor.execute(
        "INSERT INTO users (username, password) VALUES (?, ?)",
        (user_data.username, password_hash),
    )


def authenticate(*, cursor: Cursor, user_data: schema.UserCreate) -> str | None:
    row = cursor.execute(
        "SELECT username, password FROM users WHERE username = ?",
        (user_data.username,),
    ).fetchone()

    if row is None:
        return None

    username = row[0]
    password_hash = row[1]

    if not verify_password(user_data.password, password_hash):
        return None

    return create_access_token(subject=username)
