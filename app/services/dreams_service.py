import sqlite3
from collections.abc import Sequence
from datetime import datetime
import time 

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

	return session.execute(
        select(models.Dream)
        .options(joinedload(models.Dream.author))
        .where(models.Dream.id == id)
    ).unique().scalar_one_or_none()


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
		query = query.where(models.Dream.author.has(username=author))

	total = session.execute(
        select(func.count()).select_from(models.Dream).where(query.whereclause)
    ).scalar()

	dreams = session.execute(
    query.limit(limit).offset(offset)
	).unique.scalars().all()



	return dreams,total

def create(
    *, session: Session, new_dream: schema.NewDream, author: schema.UserProfile
) -> models.Dream:
    existing = session.execute(
        select(models.Dream).where(
            models.Dream.author_id == author.username,
            models.Dream.description == new_dream.description
        )
    ).first()
    
    if existing:
        raise DuplicateDatabaseException('дубликат')
    
    dream = models.Dream(
        author_id=author.username,
        description=new_dream.description,
        created_at=datetime.now()
    )
    
    session.add(dream)
    session.flush()
    session.refresh(dream, attribute_names=['author'])
    
    return dream


def delete(*, session: Session, dream_id: int) -> None:
	"""
	:session: сессия sqlalchemy
	:dream_id: идентификатор сна для удаления

	Удаляет сон из базы данных.
	"""
	dream = session.get(models.Dream,dream_id)
	if dream:
		session.delete(dream)
