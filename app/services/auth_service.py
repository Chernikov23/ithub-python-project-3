from sqlite3 import Cursor

from app import schema
from app.api.api_user import get_by_username
from app.api.exceptions import ConflictHTTPException, LoginHTTPException
from app.security import create_access_token, get_password_hash, verify_password
from app.services import users_service


def register(*, cursor: Cursor, user_data: schema.UserCreate) -> None:
	"""
	:cursor: курсор подключения к базе данных
	:user_data: данные для регистрации

	Добавляет пользователя в базу данных (хешируя пароль)
	"""
	user = users_service.get_by_username(cursor=cursor, username=user_data.username)
	if user:
		raise ConflictHTTPException(detail='Выбранный юзернейм занят')
	
	cursor.execute(
		'''
		INSERT INTO users (username, password, bio) VALUES (?, ?, ?)
		''',
		(user_data.username, get_password_hash(user_data.password), user_data.bio)
	)

	cursor.connection.commit()

def authenticate(*, cursor: Cursor, user_data: schema.UserCreate) -> str:
	"""
	Находит пользователя по юзернейму, 
	сверяет хеш переданного пароля с истинным. 
	В случае несовпадения возвращает None.
	Иначе - создает и возвращает токен доступа.
	"""
	cursor.execute(
		'''
		SELECT password FROM users WHERE username = ?
		''',
		(user_data.username,)
	)

	hashed_password = cursor.fetchone()

	if not hashed_password:
		raise LoginHTTPException()
	
	if not verify_password(plain_password=user_data.password, hashed_password=hashed_password[0]):
		raise LoginHTTPException()
	
	return create_access_token(user_data.username)
