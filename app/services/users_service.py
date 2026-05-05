from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database import models

from app import schema


def get_by_username(*, session: Session, username: str) -> schema.UserProfile | None:
	"""
	:session: сессия подключения к базе данных
	:username: уникальный юзернейм пользователя
	
	Запрашивает пользователя из базы данных. 
	Если пользователь не найден, возвращает None.
	Иначе - возвращает запись согласно схеме.
	"""	
	
	user = session.execute(
		text('SELECT username, role, bio FROM users WHERE username = :username;'),
		{'username': username}
	).fetchone()

	if not user:
		return None
	
	return schema.UserProfile(username=user[0], role=user[1], bio=user[2])

def get_by_username_orm(*, session: Session, username: str) -> models.User | None:
	"""
	:session: сессия подключения к базе данных
	:username: уникальный юзернейм пользователя
	
	Запрашивает пользователя из базы данных. 
	Если пользователь не найден, возвращает None.
	Иначе - возвращает запись согласно схеме.
	"""	
	
	user = session.execute(
		text('SELECT username, role, bio FROM users WHERE username = :username;'),
		{'username': username}
	).fetchone()

	if not user:
		return None
	
	return models.User(username=user[0], role=user[1], bio=user[2], password='')


def update(*, session: Session, username: str, update_data: schema.UserUpdate) -> schema.UserProfile | None:
	"""
	:session: сессия подключения к базе данных
	:username: уникальный юзернейм пользователя
	:update_data: данные для обновления
	
	Запрашивает пользователя из базы данных. 
	Если пользователь не найден, возвращает None.
	Иначе - возвращает обновленную запись согласно схеме. 
	"""	

	
	result = session.execute(
		text('UPDATE users SET bio = :bio WHERE username = :username;'),
		{'bio': update_data.bio, 'username': username}
	)
	
	updated = result.rowcount > 0
	
	if updated:
		session.commit()
	
	return schema.UserProfile(username=username, bio=update_data.bio, role='user') if updated else None