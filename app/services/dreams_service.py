import sqlite3
from collections.abc import Sequence

from sqlalchemy import Select, select, text
from sqlalchemy.orm import Session, joinedload

from app import schema
from app.database import SessionLocal, exceptions, models
from app.services import users_service


def get_by_id(session: Session, id: int) -> models.Dream | None:
	"""
	:session: сессия sqlalchemy
	:id: идентификатор сна

	Возвращает информацию обо сне, подгружая
	данные об авторе и лайках (favorited_by)
	из связанных таблиц (например, используя
	метод joined_load).
	"""

	raise NotImplementedError


def get_list(
	*,
	session: Session,
	limit: int,
	offset: int,
	author: str | None = None,
	search: str | None = None,
	favorited: str | None = None,
) -> tuple[Sequence[models.Dream], int]:
	"""
	:session: сессия sqlalchemy
	:limit: лимит ответа после фильтрации
	:offset: отступ ответа после фильтрации
	:author: фильтр по юзернейму автора
	:search: поиск по описанию сна
	:favorited: фильтр по любимым снам юзернейма

	Получает сны, подгружая данные об авторе 
	и лайках (favorited_by) из связанных таблиц 
	(например, используя метод joined_load).
	
	Опционально, фильтрует по автору
		Dream.author.has(User.username.ilike(f'%{author}%')),
	по описанию 
		Dream.description.ilike(f'%{search}%')
	по любимым
		Dream.favorited_by.any(User.username.ilike(f'%{favorited}%')).

	Подсчитывает количество снов после всех наложенных фильтров.
	Наконец, возвращает это число вместе с пагинированным результатом. 
	"""
	
	raise NotImplementedError



def create(
    *,
    session: Session,
    new_dream: schema.NewDream,
    author: schema.UserProfile,
) -> models.Dream:

    exists = session.query(models.Dream).filter(
        models.Dream.description == new_dream.description,
        models.Dream.author_id == author.username,
    ).first()

    if exists:
        raise exceptions.DuplicateDatabaseException(
            "Пользователь уже добавлял этот сон"
        )

    dream = models.Dream(
        description=new_dream.description,
        author_id=author.username,
    )

    session.add(dream)
    session.commit()
    session.refresh(dream)

    return dream

def delete(*, session: Session, dream_id: int) -> None:
	"""
	:session: сессия sqlalchemy
	:dream_id: идентификатор сна для удаления

	Удаляет сон из базы данных.
	"""
	
	raise NotImplementedError



def favorite(
	*, session: Session, dream: models.Dream, user: schema.UserProfile
) -> None:
	"""
	:session: сессия sqlalchemy
	:dream: ORM-модель сна для добавления в любимые
	:user: данные пользователя, желающего добавить сон в любимые

	Добавляет запись в посредническую таблицу favorited_by.
	В случае, если запись в этой таблице уже существует, выбрасывает
	исключение DuplicateDatabaseException.
	"""
	
	raise NotImplementedError


def unfavorite(
	*, session: Session, dream: models.Dream, user: schema.UserProfile
) -> None:
	"""
	:session: сессия sqlalchemy
	:dream: ORM-модель сна для добавления в любимые
	:user: данные пользователя, желающего добавить сон в любимые

	Удаляет запись из посредническую таблицу favorited_by.
	В случае, если записи в этой таблице не было, выбрасывает
	исключение NotFoundDatabaseException

	"""

	raise NotImplementedError
