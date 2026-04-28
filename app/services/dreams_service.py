import sqlite3
from collections.abc import Sequence

from sqlalchemy import Select, select
from sqlalchemy.orm import Session, joinedload

from app import schema
from app.database import models


def get_by_id(session: Session, id: int) -> models.Dream | None:
	"""
	:session: сессия sqlalchemy
	:id: идентификатор сна

	Возвращает информацию обо сне, подгружая
	данные об авторе и лайках (favorited_by)
	из связанных таблиц (например, используя
	метод joined_load).
	"""

	raise NotImplementedError


def get_list(
	*,
	session: Session,
	limit: int,
	offset: int,
	author: str | None = None,
	search: str | None = None,
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
	
	raise NotImplementedError



def create(*, session: Session, new_dream: schema.NewDream, author: schema.UserProfile) -> models.Dream:
	"""
	:session: сессия sqlalchemy
	:new_dream: данные сна для добавления
	:author: данные об авторе
	
	Добавляет новый сон, включая информацию об авторе, в базу данных.
	В случае, если такой сон уже добавлен, выбрасывает DuplicateDatabaseException.
	Иначе - возвращает ORM-объект с новым сном.
	"""

	raise NotImplementedError



def delete(*, session: Session, dream_id: int) -> None:
	"""
	:session: сессия sqlalchemy
	:dream_id: идентификатор сна для удаления

	Удаляет сон из базы данных.
	"""
	
	raise NotImplementedError
