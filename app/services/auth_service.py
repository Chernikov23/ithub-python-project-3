from sqlite3 import Cursor

from app import schema
from app.security import create_access_token, get_password_hash, verify_password


def register(*, cursor: Cursor, user_data: schema.UserCreate) -> None:
	password_hash = get_password_hash(user_data.password)

	cursor.execute(
		'INSERT INTO users(username, password) VALUES (?, ?)',
		(user_data.username, password_hash),
	)

	cursor.connection.commit()

	raise NotImplementedError


def authenticate(*, cursor: Cursor, user_data: schema.UserCreate) -> str | None:
	cursor.execute(
		'SELECT username, password FROM users WHERE username = ?',
		(user_data.username,),
	)

	user = cursor.fetchone()

	if user is None:
		return None

	if not verify_password(user_data.password, user[1]):
		return None

	return create_access_token({'sub': user[0]})

	raise NotImplementedError
