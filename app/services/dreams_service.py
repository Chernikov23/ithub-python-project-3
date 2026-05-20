import sqlite3
from collections.abc import Sequence

from sqlalchemy import Select, select
from sqlalchemy.orm import Session, joinedload

from app import schema
from app.database import models


def get_by_id(session: Session, id: int) -> models.Dream | None:
	"""
	:session: сессия sqlalchemy
	:id: идентификатор сна

	Возвращает информацию обо сне, подгружая
	данные об авторе из связанной таблицы 
	(например, используя метод joined_load).
	"""

	return session.scalar(
		select(models.Dream).options(joinedload(models.Dream.author)).where(models.Dream.id == id)
	)


def get_list(
	*,
	session: Session,
	limit: int,
	offset: int,
	author: str | None = None,
) -> tuple[Sequence[models.Dream], int]:
	"""
	:session: сессия sqlalchemy
	:limit: лимит ответа после фильтрации
	:offset: отступ ответа после фильтрации
	:author: фильтр по юзернейму автора

	Получает сны, подгружая данные об авторе
	и лайках (favorited_by) из связанных таблиц
	(например, используя метод joined_load).

	Опционально, фильтрует по автору
		Dream.author.has(User.username.ilike(f'%{author}%')),

	Подсчитывает количество снов после всех наложенных фильтров.
	Наконец, возвращает это число вместе с пагинированным результатом.
	"""

	query = select(models.Dream).options(joinedload(models.Dream.author)).order_by(models.Dream.id.desc())
	if author:
		# join user table to filter by username (case-insensitive)
		query = query.join(models.User).where(models.User.username.ilike(f'%{author}%'))
	all_items = session.scalars(query).unique().all()
	total = len(all_items)
	# apply pagination
	items = all_items[offset : offset + limit]
	return items, total


def create(
	*, session: Session, new_dream: schema.NewDream, author: schema.UserProfile
) -> models.Dream:
	"""
	:session: сессия sqlalchemy
	:new_dream: данные сна для добавления
	:author: данные об авторе

	Добавляет новый сон, включая информацию об авторе, в базу данных.
	В случае, если такой сон уже добавлен, выбрасывает DuplicateDatabaseException.
	Иначе - возвращает ORM-объект с новым сном.
	"""

	# find author user ORM object
	author_obj = session.get(models.User, author.username)
	if author_obj is None:
		raise ValueError('author not found')
	dream = models.Dream(description=new_dream.description, author=author_obj)
	session.add(dream)
	try:
		session.commit()
		session.refresh(dream)
		return dream
	except Exception as e:
		session.rollback()
		from sqlalchemy.exc import IntegrityError
		from app.database.exceptions import DuplicateDatabaseException
		if isinstance(e, IntegrityError):
			raise DuplicateDatabaseException()
		raise


def delete(*, session: Session, dream_id: int) -> None:
	"""
	:session: сессия sqlalchemy
	:dream_id: идентификатор сна для удаления

	Удаляет сон из базы данных.
	"""

	dream = session.get(models.Dream, dream_id)
	if dream is None:
		raise ValueError('not found')
	session.delete(dream)
	session.commit()
