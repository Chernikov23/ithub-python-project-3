from sqlite3 import Cursor

from app import schema


def get_by_username(*, cursor: Cursor, username: str) -> schema.UserProfile | None:
	"""
	:cursor: курсор подключения к базе данных
	:username: уникальный юзернейм пользователя
	
	Запрашивает пользователя из базы данных. 
	Если пользователь не найден, возвращает None.
	Иначе - возвращает запись согласно схеме.
	"""	
	
	raise NotImplemented


def update(*, cursor: Cursor, username: int, update_data: schema.UserUpdate) -> schema.UserProfile | None:
	"""
	:cursor: курсор подключения к базе данных
	:username: уникальный юзернейм пользователя
	:update_data: данные для обновления
	
	Запрашивает пользователя из базы данных. 
	Если пользователь не найден, возвращает None.
	Иначе - возвращает обновленную запись согласно схеме. 
	"""	

	raise NotImplemented
