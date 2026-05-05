from collections.abc import Sequence

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text

from app import schema
from app.database import models
from app.database.exceptions import DuplicateDatabaseException
from app.services import users_service as usersvc

from datetime import datetime


def _get_favorited_by(session: Session, dream_id: int) -> list[schema.UserProfile]:
    user_ids = session.execute(
        text('SELECT user_id FROM dream_favorite WHERE dream_id = :dream_id'),
        {'dream_id': dream_id}
    ).scalars().all()
    
    return [usersvc.get_by_username(session=session, username=uid) for uid in user_ids]


def get_by_id(session: Session, id: int) -> schema.Dream | None:
    dream = session.execute(
        text('SELECT id, author_id, description, created_at FROM dreams WHERE id = :id'),
        {'id': id}
    ).fetchone()

    if not dream:
        return None

    favorited_by = _get_favorited_by(session, dream[0])
    author = usersvc.get_by_username(session=session, username=dream[1])

    return schema.Dream(
        id=dream[0],
        author_id=dream[1],
        author=author,
        description=dream[2],
        created_at=datetime.fromisoformat(dream[3]).isoformat() + 'Z',
        favorited_by=favorited_by
    )


def get_list(
    *,
    session: Session,
    limit: int,
    offset: int,
    author: str | None = None,
    search: str | None = None,
    favorited: str | None = None,
) -> tuple[Sequence[schema.Dream], int]:
    query = ('SELECT * FROM dreams'
             + (' JOIN dream_favorite ON dream_favorite.dream_id = dreams.id' if favorited else '')
             + ' WHERE TRUE'
             + (' AND author_id LIKE :author' if author else '')
             + (' AND description LIKE :search' if search else '')
             + (' AND dream_favorite.user_id LIKE :favorited' if favorited else '')
             + ' ORDER BY created_at DESC'
             + (' LIMIT :limit' if limit else '')
             + (' OFFSET :offset' if offset else '')
             + ';')

    query_count = ('SELECT COUNT(*) FROM dreams'
                   + (' JOIN dream_favorite ON dream_favorite.dream_id = dreams.id' if favorited else '')
                   + ' WHERE TRUE'
                   + (' AND author_id LIKE :author' if author else '')
                   + (' AND description LIKE :search' if search else '')
                   + (' AND dream_favorite.user_id = :favorited' if favorited else '')
                   + ';')

    params = {k: v for k, v in {'author': f'%{author}%', 'search': f'%{search}%' if search else None,
                                'favorited': f'%{favorited}%' if favorited else None,
                                'limit': limit, 'offset': offset}.items() if v is not None}
    params2 = {k: v for k, v in {'author': f'%{author}%', 'search': f'%{search}%' if search else None,
                                 'favorited': f'%{favorited}%' if favorited else None}.items()
               if v is not None}

    count = session.execute(text(query_count), params2).scalar()

    dreams = []
    for row in session.execute(text(query), params).mappings().all():
        favorited_by = _get_favorited_by(session, row['id'])
        author_obj = usersvc.get_by_username(session=session, username=row['author_id'])
        
        created_str = row['created_at']
        if 'T' not in created_str:
            created_str = created_str.replace(' ', 'T') + 'Z'

        dream = schema.Dream(
            id=row['id'],
            author_id=row['author_id'],
            author=author_obj,
            description=row['description'],
            created_at=created_str,
            favorited_by=favorited_by
        )
        dreams.append(dream)

    return (dreams, count)


def create(*, session: Session, new_dream: schema.NewDream, author: schema.UserProfile) -> schema.Dream:
    try:
        dream = session.execute(
            text("INSERT INTO dreams (author_id, description, created_at) VALUES (:username, :description, datetime('now')) RETURNING id, author_id, description, created_at"),
            {'username': author.username, 'description': new_dream.description}
        ).fetchone()
        session.commit()
        
        return schema.Dream(
            id=dream[0],
            author_id=dream[1],
            author=author,
            favorited_by=[],  # только созданный сон, лайков нет
            description=dream[2],
            created_at=datetime.fromisoformat(dream[3]).isoformat() + 'Z'
        )
    except IntegrityError:
        raise DuplicateDatabaseException()


def delete(*, session: Session, dream_id: int) -> None:
    session.execute(text('DELETE FROM dreams WHERE id = :id'), {'id': dream_id})
    session.commit()


def favorite(*, session: Session, dream: schema.Dream, user: schema.UserProfile) -> None:
    try:
        session.execute(
            text('INSERT INTO dream_favorite (user_id, dream_id) VALUES (:user_id, :dream_id)'),
            {'user_id': user.username, 'dream_id': dream.id}
        )
        session.commit()
    except IntegrityError:
        raise DuplicateDatabaseException()


def unfavorite(*, session: Session, dream: schema.Dream, user: schema.UserProfile) -> None:
    session.execute(
        text('DELETE FROM dream_favorite WHERE user_id = :user_id AND dream_id = :dream_id'),
        {'user_id': user.username, 'dream_id': dream.id}
    )
    session.commit()