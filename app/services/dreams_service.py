import sqlite3
from collections.abc import Sequence

from sqlalchemy import Select, select, func
from sqlalchemy.orm import Session, joinedload

from app import schema
from app.database import models
from app.database.exceptions import DuplicateDatabaseException


def get_by_id(session: Session, id: int) -> models.Dream | None:

    stmt = select(models.Dream).options(joinedload(models.Dream.author)).where(models.Dream.id == id)
    return session.execute(stmt).unique().scalar_one_or_none()


def get_list(
    *,
    session: Session,
    limit: int,
    offset: int,
    author: str | None = None,
) -> tuple[Sequence[models.Dream], int]:

    query = select(models.Dream).options(joinedload(models.Dream.author))
    
    if author:
        query = query.where(models.Dream.author.has(models.User.username.ilike(f'%{author}%')))
    
    count_query = select(func.count()).select_from(models.Dream)
    if author:
        count_query = count_query.where(models.Dream.author.has(models.User.username.ilike(f'%{author}%')))
    
    total_count = session.execute(count_query).scalar()
    
    query = query.order_by(models.Dream.created_at.desc()).offset(offset).limit(limit)
    dreams = session.execute(query).unique().scalars().all()
    
    return dreams, total_count


def create(
    *, session: Session, new_dream: schema.NewDream, author: schema.UserProfile
) -> models.Dream:

    user = session.execute(
        select(models.User).where(models.User.username == author.username)
    ).scalar_one()
    
    existing = session.execute(
        select(models.Dream).where(
            models.Dream.author_id == author.username,
            models.Dream.description == new_dream.description
        )
    ).scalar_one_or_none()
    
    if existing:
        raise DuplicateDatabaseException("Сон уже существует")
    
    dream = models.Dream(
        author_id=author.username,
        description=new_dream.description,
        author=user
    )
    session.add(dream)
    session.flush()
    return dream


def delete(*, session: Session, dream_id: int) -> None:
    dream = session.execute(
        select(models.Dream).where(models.Dream.id == dream_id)
    ).scalar_one()
    session.delete(dream)