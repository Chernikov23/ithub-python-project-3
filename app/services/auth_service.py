from sqlalchemy.orm import Session

from app import schema
from app.database import models
from app.security import create_access_token, get_password_hash, verify_password


def register(*, session: Session, user_data: schema.UserCreate) -> None:
	"""
	:session: SQLAlchemy сессия для подключения к базе данных
	:user_data: данные для регистрации

	Добавляет пользователя в базу данных (хешируя пароль)
	"""

	user = models.User(
		username=user_data.username,
		password=get_password_hash(user_data.password),
	)
	session.add(user)
	session.commit()


def authenticate(*, session: Session, user_data: schema.UserCreate) -> str | None:
	"""
	Находит пользователя по юзернейму,
	сверяет хеш переданного пароля с истинным.
	В случае несовпадения возвращает None.
	Иначе - создает и возвращает токен доступа.
	"""

	user = session.get(models.User, user_data.username)
	if user is None:
		return None

	auth_password = user.password
	if not verify_password(user_data.password, auth_password):
		return None

	return create_access_token(subject=user_data.username)
