import sqlite3
from sqlite3 import Cursor
from app import schema
from app.database.exceptions import DuplicateDatabaseException
from app.security import create_access_token, get_password_hash, verify_password

def register(*, cursor: Cursor, user_data: schema.UserCreate) -> None:
    try:
        hashed = get_password_hash(user_data.password)
        cursor.execute(
            'INSERT INTO users (username, password) VALUES (?, ?)',
            (user_data.username, hashed),
        )
    except sqlite3.IntegrityError as exc:
        raise DuplicateDatabaseException() from exc

def authenticate(*, cursor: Cursor, user_data: schema.UserCreate) -> str | None:
    cursor.execute('SELECT password FROM users WHERE username = ?', (user_data.username,))
    row = cursor.fetchone()
    if not row:
        return None
    if not verify_password(user_data.password, row[0]):
        return None
    return create_access_token(user_data.username)