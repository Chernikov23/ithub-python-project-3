from collections.abc import Sequence

from sqlalchemy import Select, select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app import schema
from app.database import exceptions
from app.database import models


def get_by_id(session: Session, id: int) -> models.Dream | None:
	"""
	:session: сессия sqlalchemy
	:id: идентификатор сна

	Возвращает информацию обо сне, подгружая
	данные об авторе из связанной таблицы 
	(например, используя метод joined_load).
	"""

	statement = select(models.Dream).where(models.Dream.id == id).options(joinedload(models.Dream.author))
	return session.scalars(statement).unique().one_or_none()


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
	count_query = select(func.count()).select_from(models.Dream)

	if author:
		query = query.where(models.Dream.author.has(models.User.username.ilike(f'%{author}%')))
		count_query = count_query.where(models.Dream.author.has(models.User.username.ilike(f'%{author}%')))

	dreams = session.scalars(query.limit(limit).offset(offset)).unique().all()
	dreams_count = session.scalar(count_query) or 0

	return dreams, dreams_count


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

	dream = models.Dream(description=new_dream.description, author_id=author.username)
	session.add(dream)
	try:
		session.commit()
		session.refresh(dream)
	except IntegrityError as exc:
		session.rollback()
		raise exceptions.DuplicateDatabaseException from exc

	return dream


def delete(*, session: Session, dream_id: int) -> None:
	"""
	:session: сессия sqlalchemy
	:dream_id: идентификатор сна для удаления

	Удаляет сон из базы данных.
	"""

	dream = get_by_id(session, dream_id)
	if dream is None:
		return

	session.delete(dream)
	session.commit()
