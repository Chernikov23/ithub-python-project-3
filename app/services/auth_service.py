from sqlite3 import Cursor

from app import schema
from app.security import create_access_token, get_password_hash, verify_password
from app.services import users_service

def register(*, cursor: Cursor, user_data: schema.UserCreate) -> None:
	"""
	:cursor: курсор подключения к базе данных
	:user_data: данные для регистрации

	Добавляет пользователя в базу данных (хешируя пароль)
	"""
	hashed = get_password_hash(user_data.password)
	cursor.execute(
        "INSERT INTO users (username, password) VALUES (?, ?)",
        (user_data.username, hashed)
    )


def authenticate(*, cursor: Cursor, user_data: schema.UserCreate) -> str | None:
	"""
	Находит пользователя по юзернейму,
	сверяет хеш переданного пароля с истинным.
	В случае несовпадения возвращает None.
	Иначе - создает и возвращает токен доступа.
	"""
	user = users_service.get_user_with_password(cursor=cursor,username = user_data.username)
	print("FOUND USER:", user)
	if not user:
		return None
	
	username, hashed = user

	if not verify_password(user_data.password, hashed):
		return None
	
	return create_access_token(subject=username)
