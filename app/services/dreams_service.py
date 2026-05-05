from collections.abc import Sequence

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text

from app import schema
from app.database import models
from app.database.exceptions import DuplicateDatabaseException


def get_by_id(session: Session, id: int) -> models.Dream | None:
	"""
	:session: сессия sqlalchemy
	:id: идентификатор сна

	Возвращает информацию обо сне, подгружая
	данные об авторе и лайках (favorited_by)
	из связанных таблиц (например, используя
	метод joined_load).
	"""

	'''
	id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
	author_id: Mapped[str] = mapped_column(String, ForeignKey('users.username'), nullable=False)
	description: Mapped[str] = mapped_column(Text, nullable=False)
	created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
	'''

	dream = session.execute(text('SELECT id, author_id, description, created_at FROM dreams WHERE id = :id;'), {'id': id}).fetchone()

	if not dream:
		return None

	return models.Dream(id=dream[0], author_id=dream[1], description=dream[2], created_at=dream[3])


def get_list(
	*,
	session: Session,
	limit: int,
	offset: int,
	author: str | None = None,
	search: str | None = None,
	favorited: str | None = None,
) -> tuple[Sequence[models.Dream], int]:
	"""
	:session: сессия sqlalchemy
	:limit: лимит ответа после фильтрации
	:offset: отступ ответа после фильтрации
	:author: фильтр по юзернейму автора
	:search: поиск по описанию сна
	:favorited: фильтр по любимым снам юзернейма

	Получает сны, подгружая данные об авторе 
	и лайках (favorited_by) из связанных таблиц 
	(например, используя метод joined_load).
	
	Опционально, фильтрует по автору
		Dream.author.has(User.username.ilike(f'%{author}%')),
	по описанию 
		Dream.description.ilike(f'%{search}%')
	по любимым
		Dream.favorited_by.any(User.username.ilike(f'%{favorited}%')).

	Подсчитывает количество снов после всех наложенных фильтров.
	Наконец, возвращает это число вместе с пагинированным результатом. 
	"""

	query = ('SELECT * FROM dreams'
	+ (' JOIN dream_favorite ON dream_favorite.dream_id = dreams.id' if favorited else '')
	+ ' WHERE TRUE'
	+ (' AND author_id = :author' if author else '')
	+ (' AND description LIKE :search' if search else '')
	+ (' AND dream_favorite.user_id LIKE :favorited' if favorited else '')
	+ ' ORDER BY created_at ASC'
	+ (' LIMIT :limit' if limit else '')
	+ (' OFFSET :offset' if offset else '')
	+ ';')

	query_count = ('SELECT COUNT(*) FROM dreams'
	+ (' JOIN dream_favorite ON dream_favorite.dream_id = dreams.id' if favorited else '')
	+ ' WHERE TRUE'
	+ (' AND author_id = :author' if author else '')
	+ (' AND description LIKE :search' if search else '')
	+ (' AND dream_favorite.user_id = :favorited' if favorited else '')
	+ ';')

	params = {k: v for k, v in {'author': author, 'search': f'%{search}%' if search else None, 'favorited': favorited, 'limit': limit, 'offset': offset}.items() if v is not None}
	params2 = {k: v for k, v in {'author': author, 'search': f'%{search}%' if search else None, 'favorited': f'%{favorited}%' if favorited else None }.items() if v is not None}

	count = session.execute(text(query_count), params2).scalar()
	dreams = tuple([models.Dream(**row) for row in session.execute(text(query), params).mappings().all()])

	return (dreams, count)


def create(*, session: Session, new_dream: schema.NewDream, author: schema.UserProfile) -> models.Dream:
	"""
	:session: сессия sqlalchemy
	:new_dream: данные сна для добавления
	:author: данные об авторе
	
	Добавляет новый сон, включая информацию об авторе, в базу данных.
	В случае, если такой сон уже добавлен, выбрасывает DuplicateDatabaseException.
	Иначе - возвращает ORM-объект с новым сном.
	"""
	try:
		dream = session.execute(text('INSERT INTO dreams (author_id, description, created_at) VALUES (:username, :description, datetime(\'now\')) RETURNING id, author_id, description, created_at;'),
					{'username': author.username, 'description': new_dream.description}).fetchone()
		session.commit()
		return models.Dream(id=dream[0], author_id=dream[1], description=dream[2], created_at=dream[3])
	except IntegrityError:
		raise DuplicateDatabaseException()


def delete(*, session: Session, dream_id: int) -> None:
	session.execute(text('DELETE FROM dreams WHERE id = :id;'), {'id': dream_id})
	session.commit()


def favorite(
	*, session: Session, dream: models.Dream, user: schema.UserProfile
) -> None:
	"""
	:session: сессия sqlalchemy
	:dream: ORM-модель сна для добавления в любимые
	:user: данные пользователя, желающего добавить сон в любимые

	Добавляет запись в посредническую таблицу favorited_by.
	В случае, если запись в этой таблице уже существует, выбрасывает
	исключение DuplicateDatabaseException.
	"""
	
	try:
		session.execute(text('INSERT INTO dream_favorite (user_id, dream_id) VALUES (:user_id, :dream_id);'),
					{'user_id': user.username, 'dream_id': dream.id})
		session.commit()
	except IntegrityError:
		raise DuplicateDatabaseException()


def unfavorite(
	*, session: Session, dream: models.Dream, user: schema.UserProfile
) -> None:
	"""
	:session: сессия sqlalchemy
	:dream: ORM-модель сна для добавления в любимые
	:user: данные пользователя, желающего добавить сон в любимые

	Удаляет запись из посредническую таблицу favorited_by.
	В случае, если записи в этой таблице не было, выбрасывает
	исключение NotFoundDatabaseException

	"""

	session.execute(text('DELETE FROM dream_favorite WHERE user_id = :user_id AND dream_id = :dream_id;'),
					{'user_id': user.username, 'dream_id': dream.id})
	
	session.commit()