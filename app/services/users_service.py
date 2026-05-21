from sqlalchemy.orm import Session

from app import schema
from app.database import models


def get_by_username(*, session: Session, username: str) -> schema.UserProfile | None:
	"""
	:session: SQLAlchemy сессия для подключения к базе данных
	:username: уникальный юзернейм пользователя

	Запрашивает пользователя из базе данных.
	Если пользователь не найден, возвращает None.
	Иначе - возвращает запись согласно схеме.
	"""

	user = session.get(models.User, username)
	if user is None:
		return None
	return schema.UserProfile(username=user.username)
