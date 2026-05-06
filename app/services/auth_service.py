from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

import app.security as security
from app import schema


def register(*, session: Session, user_data: schema.UserCreate) -> bool:
	"""
	:session: сессия подключения к базе данных
	:user_data: данные для регистрации

	Добавляет пользователя в базу данных (хешируя пароль)
	"""

	try:
		session.execute(
			text(
				"INSERT INTO users (username, password, bio, role) VALUES (:username, :password, :bio, 'user');"
			),
			{
				'username': user_data.username,
				'password': security.get_password_hash(user_data.password),
				'bio': user_data.bio,
			},
		)
		session.commit()
	except IntegrityError:
		session.rollback()
		return False

	return True


def set_role(*, session: Session, username: schema.UsernameType, role: schema.RoleType) -> bool:
	try:
		session.execute(
			text('UPDATE users SET role = :role WHERE username = :username;'),
			{'username': username, 'role': role},
		)
		session.commit()
	except IntegrityError:
		session.rollback()
		return False

	return True


def authenticate(*, session: Session, user_data: schema.UserCreate) -> str | None:
	"""
	Находит пользователя по юзернейму,
	сверяет хеш переданного пароля с истинным.
	В случае несовпадения возвращает None.
	Иначе - создает и возвращает токен доступа.
	"""

	result = session.execute(
		text('SELECT password FROM users WHERE username = :username;'),
		{'username': user_data.username},
	).fetchone()

	if not result:
		return None

	if not security.verify_password(user_data.password, result[0]):
		return None

	return security.create_access_token(user_data.username)
