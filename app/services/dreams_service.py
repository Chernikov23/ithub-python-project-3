import sqlite3
from collections.abc import Sequence

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql.expression import desc
from sqlalchemy.exc import IntegrityError

from app import schema
from app.database import SessionLocal, exceptions, models


def get_by_id(session: Session, id: int) -> models.Dream | None:
	print(id)
	return session.scalar(
		select(models.Dream)
		.options(
			joinedload(models.Dream.author),
			joinedload(models.Dream.favorited_by),
		)
		.filter_by(id=id)
	)


def get_list(
	*,
	session: Session,
	limit: int,
	offset: int,
	author: str | None = None,
	search: str | None = None,
	favorited: str | None = None,
) -> tuple[Sequence[models.Dream], int]:
	query = select(models.Dream).options(
		joinedload(models.Dream.author),
		joinedload(models.Dream.favorited_by),
	)

	if author:
		query = query.filter(models.Dream.author.has(models.User.username.ilike(f'%{author}%')))
	if search:
		query = query.filter(models.Dream.description.ilike(f'%{search}%'))
	if favorited:
		query = query.filter(
			models.Dream.favorited_by.any(models.User.username.ilike(f'%{favorited}%'))
		)

	return get_paginated_list(session=session, limit=limit, offset=offset, query=query)


def get_paginated_list(
	*, session: Session, limit: int, offset: int, query: Select[tuple[models.Dream]]
) -> tuple[Sequence[models.Dream], int]:
	query_list = query.order_by(desc(models.Dream.created_at)).limit(limit).offset(offset)

	with SessionLocal() as db_count:
		query_count = select(func.count()).select_from(query.subquery())
		Dreams = session.scalars(query_list)
		count = db_count.scalar(query_count)

	return Dreams.unique().all(), count or 0


def create(*, session: Session, new_dream: schema.NewDream, author: models.User) -> models.Dream:
	try:
		dream_to_create = models.Dream(
			description=new_dream.description,
			author_id=author.username,
		)

		session.add(dream_to_create)
		session.commit()
		session.refresh(dream_to_create)

		return dream_to_create
	except (sqlite3.IntegrityError, IntegrityError):
		session.rollback()
		raise exceptions.DuplicateDreamException


def delete(*, session: Session, dream_id: int) -> None:
	dream = session.execute(select(models.Dream).where(models.Dream.id == dream_id)).scalar()
	session.delete(dream)
	session.commit()


def favorite(
	*, session: Session, dream: models.Dream, user: models.User, favorite: bool = True
) -> None:
	if favorite:
		dream.favorited_by.append(user)
	else:
		dream.favorited_by.remove(user)

	session.merge(dream)
	session.commit()
