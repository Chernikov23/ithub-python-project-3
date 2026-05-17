import sqlite3
from collections.abc import Sequence

from sqlalchemy import text
from sqlalchemy import Select, select, func
from sqlalchemy.orm import Session, joinedload

from app import schema
from app.database import models
from app.database.exceptions import DuplicateDatabaseException


def get_by_id(session: Session, id: int) -> models.Dream | None:
    """
    :session: сессия sqlalchemy
    :id: идентификатор сна

    Возвращает информацию обо сне, подгружая
    данные об авторе из связанной таблицы
    (например, используя метод joined_load).
    """
    return session.scalar(
        select(models.Dream)
        .options(joinedload(models.Dream.author))
        .where(models.Dream.id == id)
    )


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

    query = select(models.Dream).options(joinedload(models.Dream.author))

    if author:
        query = query.where(
            models.Dream.author.has(models.User.username.ilike(f"%{author}%"))
        )

    count_query = select(func.count()).select_from(query.subquery())
    total_count = session.scalar(count_query)

    dreams = (
        session.scalars(
            query.order_by(models.Dream.created_at.desc()).offset(offset).limit(limit)
        )
        .unique()
        .all()
    )

    return dreams, total_count or 0


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

    existing = session.scalar(
        select(models.Dream)
        .where(models.Dream.author_id == author.username)
        .where(models.Dream.description == new_dream.description)
    )

    if existing:
        raise DuplicateDatabaseException("Пользователь уже добавлял этот сон")

    dream = session.execute(
        text(
            "INSERT INTO dreams (author_id, description, created_at) VALUES (:username, :description, datetime('now')) RETURNING id, created_at"
        ),
        {"username": author.username, "description": new_dream.description},
    ).fetchone()

    return session.scalar(
        select(models.Dream)
        .options(joinedload(models.Dream.author))
        .where(models.Dream.id == dream.id)
    )


def delete(*, session: Session, dream_id: int) -> None:
    """
    :session: сессия sqlalchemy
    :dream_id: идентификатор сна для удаления

    Удаляет сон из базы данных.
    """
    session.execute(select(models.Dream).where(models.Dream.id == dream_id))
    session.delete(session.get(models.Dream, dream_id))
