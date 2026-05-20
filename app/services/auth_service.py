import sqlite3
from sqlite3 import Cursor

from app import schema
from app.database.exceptions import DuplicateDatabaseException
from app.security import create_access_token, get_password_hash, verify_password


def register(*, cursor: Cursor, user_data: schema.UserCreate) -> None:
	"""
	Добавляет пользователя в sqlite через переданный курсор.
	"""
	try:
		hashed = get_password_hash(user_data.password)
		cursor.execute(
			'INSERT INTO users (username, password) VALUES (?, ?)',
			(user_data.username, hashed),
		)
	except sqlite3.IntegrityError as exc:
		# если такая запись уже есть — кидаем специальное исключение
		raise DuplicateDatabaseException() from exc


def authenticate(*, cursor: Cursor, user_data: schema.UserCreate) -> str | None:
	"""
	Проверяет пароль и возвращает токен или None.
	"""
	cursor.execute('SELECT password FROM users WHERE username = ?', (user_data.username,))
	row = cursor.fetchone()
	if not row:
		return None
	stored_hashed = row[0]
	if not verify_password(user_data.password, stored_hashed):
		return None
	# вернём токен
	return create_access_token(user_data.username)
