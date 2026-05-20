from collections.abc import Sequence
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app import schema
from app.database import models
from app.database.exceptions import DuplicateDatabaseException


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

	stmt = select(models.Dream).options(joinedload(models.Dream.author))
	count_stmt = select(func.count(models.Dream.id))

	if author:
		filter_cond = models.Dream.author.has(models.User.username.ilike(f'%{author}%'))
		stmt = stmt.where(filter_cond)
		count_stmt = count_stmt.where(filter_cond)

	total = session.execute(count_stmt).scalar() or 0

	stmt = stmt.order_by(models.Dream.id.desc()).limit(limit).offset(offset)
	dreams = session.execute(stmt).unique().scalars().all()

	return dreams, total


def create(
	*, session: Session, new_dream: schema.NewDream, author: schema.UserProfile
) -> models.Dream:
	existing = (
		session.execute(
			select(models.Dream).where(
				models.Dream.author_id == author.username,
				models.Dream.description == new_dream.description,
			)
		)
		.scalars()
		.first()
	)

	if existing:
		raise DuplicateDatabaseException('Такой сон уже существует')

	dream = models.Dream(
		author_id=author.username, description=new_dream.description, created_at=datetime.now(UTC)
	)

	session.add(dream)
	session.commit()
	session.refresh(dream)

	return dream


def delete(*, session: Session, dream_id: int) -> None:

	dream = session.get(models.Dream, dream_id)
	if dream:
		session.delete(dream)
		session.commit()
