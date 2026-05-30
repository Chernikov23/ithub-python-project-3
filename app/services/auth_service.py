from sqlite3 import Cursor
from typing import Protocol

from app import schema
from app.security import create_access_token, get_password_hash, verify_password


class Credentials(Protocol):
	username: str
	password: str


def register(*, cursor: Cursor, user_data: schema.UserCreate) -> None:
	hashed_password = get_password_hash(user_data.password)

	cursor.execute(
		'INSERT INTO users (username, password, bio) VALUES (?, ?, ?)',
		(user_data.username, hashed_password, user_data.bio),
	)


def authenticate(*, cursor: Cursor, user_data: Credentials) -> str | None:
	row = cursor.execute(
		'SELECT username, password FROM users WHERE username = ?',
		(user_data.username,),
	).fetchone()

	if row is None:
		return None

	if not verify_password(user_data.password, row[1]):
		return None

	return create_access_token(row[0])
