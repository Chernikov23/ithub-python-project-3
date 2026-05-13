import sqlite3
from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app import schema
from app.database import models
from app.database.exceptions import DuplicateDatabaseException


def get_by_id(session: Session, id: int) -> models.Dream | None:
	"""
	:session: сессия sqlalchemy
	:id: идентификатор сна

	Возвращает информацию обо сне, подгружая
	данные об авторе из связанной таблицы.
	"""

	stmt = (
		select(models.Dream).options(joinedload(models.Dream.author)).where(models.Dream.id == id)
	)
	return session.scalars(stmt).unique().one_or_none()


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

	Получает сны, подгружая данные об авторе.
	Опционально, фильтрует по автору.
	Подсчитывает количество снов после всех наложенных фильтров.
	Возвращает кортеж (сны, общее количество).
	"""

	stmt = select(models.Dream).options(joinedload(models.Dream.author))
	count_stmt = select(func.count(models.Dream.id))

	if author is not None:
		filter_clause = models.Dream.author.has(models.User.username.ilike(f'%{author}%'))
		stmt = stmt.where(filter_clause)
		count_stmt = count_stmt.where(filter_clause)

	total = session.scalar(count_stmt) or 0

	stmt = (
		stmt.order_by(models.Dream.created_at.desc(), models.Dream.id.desc())
		.limit(limit)
		.offset(offset)
	)
	dreams = session.scalars(stmt).unique().all()

	return dreams, total


def create(
	*, session: Session, new_dream: schema.NewDream, author: schema.UserProfile
) -> models.Dream:
	"""
	:session: сессия sqlalchemy
	:new_dream: данные сна для добавления
	:author: данные об авторе

	Добавляет новый сон в базу данных.
	В случае, если такой сон уже добавлен, выбрасывает DuplicateDatabaseException.
	Иначе - возвращает ORM-объект с новым сном.
	"""

	dream = models.Dream(
		description=new_dream.description,
		author_id=author.username,
	)
	session.add(dream)

	try:
		session.commit()
	except (IntegrityError, sqlite3.IntegrityError) as exc:
		session.rollback()
		raise DuplicateDatabaseException('Сон с таким описанием уже существует') from exc

	session.refresh(dream)
	return dream


def delete(*, session: Session, dream_id: int) -> None:
	"""
	:session: сессия sqlalchemy
	:dream_id: идентификатор сна для удаления

	Удаляет сон из базы данных.
	"""

	dream = session.get(models.Dream, dream_id)
	if dream is None:
		return
	session.delete(dream)
	session.commit()