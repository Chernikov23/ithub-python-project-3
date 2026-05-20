from collections.abc import Sequence
from datetime import datetime
from sqlalchemy import select, func, desc
from sqlalchemy.orm import Session, joinedload
from app import schema
from app.database import models
from app.database.exceptions import DuplicateDatabaseException

def get_by_id(session: Session, id: int) -> models.Dream | None:
	session.expire_all()
	return session.execute(
		select(models.Dream).where(models.Dream.id == id)
	).unique().scalar_one_or_none()


def get_list(
	*,
	session: Session,
	limit: int,
	offset: int,
	author: str | None = None,
) -> tuple[Sequence[models.Dream], int]:
	session.expire_all()

	query = select(models.Dream).options(joinedload(models.Dream.author)).order_by(models.Dream.id.desc())
	count_query = select(func.count(models.Dream.id))

	if author:
		query = query.where(models.Dream.author_id.ilike(f"%{author}%"))
		count_query = count_query.where(models.Dream.author_id.ilike(f"%{author}%"))

	total = session.execute(count_query).scalar() or 0
	dreams = session.execute(query.limit(limit).offset(offset)).unique().scalars().all()

	return dreams, total


def create(
	*, session: Session, new_dream: schema.NewDream, author: schema.UserProfile
) -> models.Dream:
	existing = session.execute(
		select(models.Dream).where(
			models.Dream.author_id == author.username,
			models.Dream.description == new_dream.description
		)
	).unique().first()
	
	if existing:
		raise DuplicateDatabaseException('дубликат')
	
	dream = models.Dream(
		author_id=author.username,
		description=new_dream.description,
		created_at=datetime.now()
	)
	
	session.add(dream)
	session.commit()
	session.expire_all()
	
	return dream


def delete(*, session: Session, dream_id: int) -> None:
	dream = session.get(models.Dream, dream_id)
	if dream:
		session.delete(dream)
		session.commit()
		session.expire_all()
