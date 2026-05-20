
from datetime import datetime

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import schema
from app.database.exceptions import DuplicateDatabaseException
from app.services import users_service as usersvc


def get_by_id(*, session: Session, id: schema.IndexType) -> schema.Dream | None:
	dream = session.execute(
		text('SELECT id, author, description, created_at FROM dreams WHERE id = :id'), {'id': id}
	).fetchone()

	if not dream:
		return None

	author = usersvc.get_by_username(session=session, username=dream[1])

	favorited_by = (
		session.execute(
			text('SELECT username FROM dream_favorite WHERE dream_id = :id;'), {'id': id}
		)
		.scalars()
		.all()
	)

	return schema.Dream(
		id=dream[0],
		author=schema.UserProfile(username=author.username, bio=author.bio),
		description=dream[2],
		created_at=datetime.fromisoformat(dream[3]).strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
		favorited_by=favorited_by,
	)

def update_by_id(*, session: Session, id: schema.IndexType, update_data: schema.NewDream) -> schema.Dream | None:
	dream = session.execute(
		text('UPDATE dreams SET description = :description WHERE id = :id RETURNING author, created_at;'),
		{'description': update_data.description, 'id': id},
	).fetchone()

	if not dream:
		return None

	author = usersvc.get_by_username(session=session, username=dream[0])

	favorited_by = (
		session.execute(
			text('SELECT username FROM dream_favorite WHERE dream_id = :id'), {'id': id}
		)
		.scalars()
		.all()
	)

	return schema.Dream(id=id, description=update_data.description,
					 author=schema.UserProfile(username=author.username, bio=author.bio),
					 created_at=datetime.fromisoformat(dream[1]).strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
					 favorited_by=favorited_by)


def get_list(
	*,
	session: Session,
	limit: schema.CountType,
	offset: schema.IndexType,
	author: str | None = None,
	search: str | None = None,
	favorited: str | None = None,
) -> schema.MultipleDreams:
	query = (
		'SELECT id FROM dreams'
		+ (' JOIN dream_favorite ON dream_favorite.dream_id = dreams.id' if favorited else '')
		+ ' WHERE TRUE'
		+ (' AND author LIKE :author' if author else '')
		+ (' AND description LIKE :search' if search else '')
		+ (' AND dream_favorite.username LIKE :favorited' if favorited else '')
		+ ' ORDER BY created_at DESC'
		+ (' LIMIT :limit' if limit else '')
		+ (' OFFSET :offset' if offset else '')
		+ ';'
	)

	count = (
		'SELECT COUNT(id) FROM dreams'
		+ (' JOIN dream_favorite ON dream_favorite.dream_id = dreams.id' if favorited else '')
		+ ' WHERE TRUE'
		+ (' AND author LIKE :author' if author else '')
		+ (' AND description LIKE :search' if search else '')
		+ (' AND dream_favorite.username LIKE :favorited' if favorited else '')
		+ ';'
	)

	query_params = {
		k: v
		for k, v in {
			'author': f'%{author}%',
			'search': f'%{search}%' if search else None,
			'favorited': f'%{favorited}%' if favorited else None,
			'limit': limit,
			'offset': offset,
		}.items()
		if v is not None
	}
	count_params = {
		k: v
		for k, v in {
			'author': f'%{author}%',
			'search': f'%{search}%' if search else None,
			'favorited': f'%{favorited}%' if favorited else None,
		}.items()
		if v is not None
	}

	dreams_count = session.execute(text(count), count_params).scalar()

	dreams = []

	for id in session.execute(text(query), query_params).scalars().all():
		dreams.append(get_by_id(session=session, id=id))

	return schema.MultipleDreams(dreams=dreams, dreams_count=dreams_count)


def create(
	*, session: Session, new_dream: schema.NewDream, author: schema.UserProfile
) -> schema.Dream:
	try:
		dream = session.execute(
			text(
				"INSERT INTO dreams (author, description, created_at) VALUES (:username, :description, datetime('now')) RETURNING id, created_at"
			),
			{'username': author.username, 'description': new_dream.description},
		).fetchone()
	except IntegrityError:
		session.rollback()
		raise DuplicateDatabaseException()

	return schema.Dream(
		id=dream[0],
		author=author,
		favorited_by=[],
		description=new_dream.description,
		created_at=datetime.fromisoformat(dream[1]).strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
	)


def delete(*, session: Session, dream_id: schema.IndexType) -> None:
	session.execute(
		text('DELETE FROM dream_favorite WHERE dream_id = :dream_id'), {'dream_id': dream_id}
	)
	session.execute(text('DELETE FROM dreams WHERE id = :id'), {'id': dream_id})


def delete_by_username(*, session: Session, username: schema.UsernameType) -> None:
	session.execute(
		text('DELETE FROM dream_favorite WHERE username = :username'), {'username': username}
	)
	session.execute(text('DELETE FROM dreams WHERE author = :username'), {'username': username})


def favorite(*, session: Session, dream: schema.Dream, user: schema.UserProfile) -> None:
	session.execute(
		text(
			'INSERT INTO dream_favorite (username, dream_id) VALUES (:username, :dream_id) ON CONFLICT (username, dream_id) DO NOTHING;'
		),
		{'username': user.username, 'dream_id': dream.id},
	)


def unfavorite(*, session: Session, dream: schema.Dream, user: schema.UserProfile) -> None:
	session.execute(
		text('DELETE FROM dream_favorite WHERE username = :username AND dream_id = :dream_id'),
		{'username': user.username, 'dream_id': dream.id},
	)
