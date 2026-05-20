from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app import schema
from app.database import models
from app.database.exceptions import DuplicateDatabaseException


def get_by_id(session: Session, id: int) -> models.Dream | None:
    query = (
        select(models.Dream)
        .options(joinedload(models.Dream.author))
        .where(models.Dream.id == id)
    )

    return session.scalar(query)


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

    count_query = select(func.count(models.Dream.id))

    if author:
        author_filter = models.Dream.author.has(
            models.User.username.ilike(f"%{author}%")
        )

        query = query.where(author_filter)
        count_query = count_query.where(author_filter)

    dreams_count = session.scalar(count_query) or 0

    dreams = session.scalars(
        query.limit(limit).offset(offset),
    ).unique().all()

    return dreams, dreams_count


def create(
    *,
    session: Session,
    new_dream: schema.NewDream,
    author: schema.UserProfile,
) -> models.Dream:
    dream = models.Dream(
        description=new_dream.description,
        author_id=author.username,
    )

    session.add(dream)

    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise DuplicateDatabaseException

    session.refresh(dream)

    return dream


def delete(*, session: Session, dream_id: int) -> None:
    dream = get_by_id(session, dream_id)

    if dream is None:
        return

    session.delete(dream)
    session.commit()
