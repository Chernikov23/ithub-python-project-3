from sqlite3 import Cursor

from app import schema
from app.security import create_access_token, get_password_hash, verify_password


def register(*, cursor: Cursor, user_data: schema.UserCreate) -> None:
	"""
	:cursor: курсор подключения к базе данных
	:user_data: данные для регистрации

	Добавляет пользователя в базу данных (хешируя пароль)
	"""

	# insert user with hashed password
	hashed = get_password_hash(user_data.password)
	cursor.execute(
		"INSERT INTO users (username, password) VALUES (?, ?)",
		(user_data.username, hashed),
	)


def authenticate(*, cursor: Cursor, user_data: schema.UserCreate) -> str | None:
	"""
	Находит пользователя по юзернейму,
	сверяет хеш переданного пароля с истинным.
	В случае несовпадения возвращает None.
	Иначе - создает и возвращает токен доступа.
	"""

	cursor.execute('SELECT password FROM users WHERE username = ?', (user_data.username,))
	row = cursor.fetchone()
	if not row:
		return None
	stored_hashed = row[0]
	if not verify_password(user_data.password, stored_hashed):
		return None
	return create_access_token(user_data.username)
