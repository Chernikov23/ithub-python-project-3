from sqlite3 import Cursor

from app import schema
from app.security import create_access_token, get_password_hash, verify_password


def register(*, cursor: Cursor, user_data: schema.UserCreate) -> None:
    hashed_password = get_password_hash(user_data.password)
    cursor.execute(
        "INSERT INTO users (username, password) VALUES (?, ?)",
        (user_data.username, hashed_password)
    )


def authenticate(*, cursor: Cursor, user_data: schema.UserCreate) -> str | None:

    cursor.execute("SELECT password FROM users WHERE username = ?", (user_data.username,))
    row = cursor.fetchone()
    if not row:
        return None
    
    hashed_password = row[0]
    if not verify_password(user_data.password, hashed_password):
        return None
    
    return create_access_token(user_data.username)