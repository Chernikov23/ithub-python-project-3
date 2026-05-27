import sqlite3
from collections.abc import Sequence

from sqlalchemy import Select, select
from sqlalchemy.orm import Session, joinedload

from app import schema
from app.database import models


def get_by_id(session: Session, id: int) -> models.Dream | None:
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
	query = select(models.Dream).options(joinedload(models.Dream.author)).order_by(models.Dream.id.desc())
	if author:
		query = query.join(models.User).where(models.User.username.ilike(f'%{author}%'))
	all_items = session.scalars(query).unique().all()
	total = len(all_items)
	items = all_items[offset : offset + limit]
	return items, total


def create(
	*, session: Session, new_dream: schema.NewDream, author: schema.UserProfile
) -> models.Dream:
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
	dream = session.get(models.Dream, dream_id)
	if dream is None:
		raise ValueError('not found')
	session.delete(dream)
	session.commit()
