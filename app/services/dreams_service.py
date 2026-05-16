import sqlite3
from collections.abc import Sequence

from sqlalchemy import Select, select
from sqlalchemy.orm import Session, joinedload

from app import schema
from app.database import models


def get_by_id(session: Session, id: int) -> models.Dream | None:
	query = (
		select(models.Dream)
		.options(joinedload(models.Dream.author))
		.where(models.Dream.id == id)
	)

	return session.scalar(query)

	raise NotImplementedError


def get_list(
	*,
	session: Session,
	limit: int,
	offset: int,
	author: str | None = None,
) -> tuple[Sequence[models.Dream], int]:
	query = (
		select(models.Dream)
		.options(joinedload(models.Dream.author))
		.order_by(models.Dream.created_at.desc())
	)

	if author:
		query = query.where(
			models.Dream.author.has(models.User.username.ilike(f'%{author}%'))
		)

	all_items = session.scalars(query).unique().all()
	count = len(all_items)

	items = session.scalars(
		query.limit(limit).offset(offset)
	).unique().all()

	return items, count

	raise NotImplementedError


def create(
	*, session: Session, new_dream: schema.NewDream, author: schema.UserProfile
) -> models.Dream:
	user = session.scalar(
		select(models.User).where(models.User.username == author.username)
	)

	existing = session.scalar(
		select(models.Dream).where(
			models.Dream.description == new_dream.description,
			models.Dream.author_id == user.id,
		)
	)

	if existing is not None:
		raise DuplicateDatabaseException

	dream = models.Dream(
		description=new_dream.description,
		author=user,
	)

	session.add(dream)
	session.commit()
	session.refresh(dream)

	return dream

	raise NotImplementedError


def delete(*, session: Session, dream_id: int) -> None:
	dream = session.get(models.Dream, dream_id)

	if dream is not None:
		session.delete(dream)
		session.commit()

	raise NotImplementedError
