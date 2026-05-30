from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app import schema
from app.database import exceptions, models


def get_by_id(session: Session, id: int) -> models.Dream | None:
	statement = (
		select(models.Dream)
		.options(
			joinedload(models.Dream.author),
			joinedload(models.Dream.favorited_by),
		)
		.where(models.Dream.id == id)
	)

	return session.scalars(statement).unique().one_or_none()


def get_list(
	*,
	session: Session,
	limit: int,
	offset: int,
	author: str | None = None,
	search: str | None = None,
	favorited: str | None = None,
) -> tuple[Sequence[models.Dream], int]:
	statement = select(models.Dream)

	if author:
		statement = statement.where(
			models.Dream.author.has(models.User.username.ilike(f'%{author}%'))
		)

	if search:
		statement = statement.where(models.Dream.description.ilike(f'%{search}%'))

	if favorited:
		statement = statement.where(
			models.Dream.favorited_by.any(models.User.username.ilike(f'%{favorited}%'))
		)

	count_statement = select(func.count()).select_from(statement.subquery())
	dreams_count = session.scalar(count_statement) or 0

	paginated = (
		statement.options(
			joinedload(models.Dream.author),
			joinedload(models.Dream.favorited_by),
		)
		.order_by(models.Dream.created_at.desc(), models.Dream.id.desc())
		.limit(limit)
		.offset(offset)
	)

	dreams = session.scalars(paginated).unique().all()

	return dreams, dreams_count


def create(
	*, session: Session, new_dream: schema.NewDream, author: schema.UserProfile
) -> models.Dream:
	dream = models.Dream(description=new_dream.description, author_id=author.username)

	session.add(dream)

	try:
		session.commit()
	except IntegrityError as error:
		session.rollback()
		raise exceptions.DuplicateDatabaseException from error

	session.refresh(dream)

	return dream


def delete(*, session: Session, dream_id: int) -> None:
	dream = session.get(models.Dream, dream_id)

	if dream is None:
		raise exceptions.NotFoundDatabaseException

	session.delete(dream)
	session.commit()


def favorite(*, session: Session, dream: models.Dream, user: schema.UserProfile) -> None:
	user_object = session.get(models.User, user.username)

	if user_object is None:
		raise exceptions.NotFoundDatabaseException

	if user_object in dream.favorited_by:
		raise exceptions.DuplicateDatabaseException

	dream.favorited_by.append(user_object)
	session.commit()
	session.refresh(dream)


def unfavorite(*, session: Session, dream: models.Dream, user: schema.UserProfile) -> None:
	user_object = session.get(models.User, user.username)

	if user_object is None or user_object not in dream.favorited_by:
		raise exceptions.NotFoundDatabaseException

	dream.favorited_by.remove(user_object)
	session.commit()
	session.refresh(dream)
