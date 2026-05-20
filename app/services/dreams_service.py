import sqlite3
from collections.abc import Sequence

from sqlalchemy import Select, select, func
from sqlalchemy.orm import Session, joinedload

from app import schema
from app.database import models
from app.database.exceptions import DuplicateDatabaseException


def get_by_id(session: Session, id: int) -> models.Dream | None:
	"""
	:session: сессия sqlalchemy
	:id: идентификатор сна

	Возвращает информацию обо сне, подгружая
	данные об авторе из связанной таблицы 
	(например, используя метод joined_load).
	"""

	return session.scalar(
		select(models.Dream)
		.options(joinedload(models.Dream.author))
		.where(models.Dream.id == id)
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

	query = select(models.Dream).options(joinedload(models.Dream.author))
	
	if author:
		query = query.where(models.Dream.author.has(models.User.username.ilike(f'%{author}%')))
	
	count_query = select(func.count()).select_from(query.subquery())
	total = session.scalar(count_query) or 0
	
	dreams = session.scalars(
		query.order_by(models.Dream.created_at.desc())
		.offset(offset)
		.limit(limit)
	).unique().all()
	
	return dreams, total


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

	user = session.scalar(
		select(models.User).where(models.User.username == author.username)
	)
	
	if not user:
		raise ValueError("User not found")
	
	existing = session.scalar(
		select(models.Dream).where(
			models.Dream.author_id == user.username,
			models.Dream.description == new_dream.description
		)
	)
	
	if existing:
		raise DuplicateDatabaseException("Сон с таким описанием уже существует")
	
	dream = models.Dream(
		description=new_dream.description,
		author=user
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

	dream = session.get(models.Dream, dream_id)
	if dream:
		session.delete(dream)
		session.commit()