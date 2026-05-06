from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database import models
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database import models

from app import schema
from app.services import dreams_service as dreamsvc


def get_by_username(*, session: Session, username: str) -> schema.UserAccount | None:
	"""
	:session: сессия подключения к базе данных
	:session: сессия подключения к базе данных
	:username: уникальный юзернейм пользователя
	
	Запрашивает пользователя из базы данных. 
	Если пользователь не найден, возвращает None.
	Иначе - возвращает запись согласно схеме.
	"""	
	
	user = session.execute(
		text('SELECT username, bio, role FROM users WHERE username = :username;'),
		{'username': username}
	).fetchone()
	
	return schema.UserAccount(username=user[0], bio=user[1], role=user[2]) if user else None


def update(*, session: Session, username: schema.UsernameType, update_data: schema.UserUpdate) -> schema.UserProfile | None:
	"""
	:session: сессия подключения к базе данных
	:session: сессия подключения к базе данных
	:username: уникальный юзернейм пользователя
	:update_data: данные для обновления
	
	Запрашивает пользователя из базы данных. 
	Если пользователь не найден, возвращает None.
	Иначе - возвращает обновленную запись согласно схеме. 
	"""	

	
	updated = session.execute(
		text('UPDATE users SET bio = :bio WHERE username = :username;'),
		{'bio': update_data.bio, 'username': username}
	).rowcount > 0
	
	return schema.UserProfile(username=username, bio=update_data.bio) if updated else None


def delete(*, session: Session, username: schema.UsernameType) -> None:
	dreamsvc.delete_by_username(session=session, username=username)
	session.execute('DELETE FROM users WHERE username = :username;')