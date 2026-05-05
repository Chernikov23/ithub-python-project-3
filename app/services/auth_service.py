from sqlite3 import Cursor, IntegrityError
import app.security as security

from app import schema

def register(*, cursor: Cursor, user_data: schema.UserCreate) -> bool:
	"""
	:cursor: курсор подключения к базе данных
	:user_data: данные для регистрации

	Добавляет пользователя в базу данных (хешируя пароль)
	"""

	try:
		cursor.execute('INSERT INTO users (username, password, bio, role) VALUES (?, ?, ?, \'user\');',
					(user_data.username, security.get_password_hash(user_data.password), user_data.bio))
		cursor.connection.commit()
	except IntegrityError:
		return False
	
	return True


def authenticate(*, cursor: Cursor, user_data: schema.UserCreate) -> str | None:
	"""
	Находит пользователя по юзернейму, 
	сверяет хеш переданного пароля с истинным. 
	В случае несовпадения возвращает None.
	Иначе - создает и возвращает токен доступа.
	"""

	hash = cursor.execute('SELECT password FROM users WHERE username = ?;', (user_data.username,)).fetchone()

	if not hash:
		return None
	
	if not security.verify_password(user_data.password, hash[0]):
		return None
	
	return security.create_access_token(user_data.username)