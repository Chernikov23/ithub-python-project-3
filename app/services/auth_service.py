from sqlite3 import Cursor

from app import schema
from app.security import create_access_token, get_password_hash, verify_password


def register(*, cursor: Cursor, user_data: schema.UserCreate) -> None:
	"""
	:cursor: курсор подключения к базе данных
	:user_data: данные для регистрации

	Добавляет пользователя в базу данных (хешируя пароль)
	"""

	hashed_password = get_password_hash(user_data.password)
	cursor.execute(
		'INSERT INTO users (username, password) VALUES (?, ?)',
		(user_data.username, hashed_password),
	)


def authenticate(*, cursor: Cursor, username: str, password: str) -> str | None:
	"""
	Находит пользователя по юзернейму,
	сверяет хеш переданного пароля с истинным.
	В случае несовпадения возвращает None.
	Иначе - создает и возвращает токен доступа.
	"""

	row = cursor.execute(
		'SELECT username, password FROM users WHERE username = ?',
		(username,),
	).fetchone()

	if row is None:
		return None

	if not verify_password(password, row[1]):
		return None

	return create_access_token(row[0])