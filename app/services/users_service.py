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
	cursor.execute(
		'''
		SELECT username, bio FROM users WHERE username = ?
		''',
		(username,)
	)
	user = cursor.fetchone()
	
	if not user:
		return None
	
	return schema.UserProfile(username=user[0], bio=user[1])

def update(*, cursor: Cursor, username: str, update_data: schema.UserUpdate) -> schema.UserProfile | None:
	"""
	:cursor: курсор подключения к базе данных
	:username: уникальный юзернейм пользователя
	:update_data: данные для обновления
	
	Запрашивает пользователя из базы данных. 
	Если пользователь не найден, возвращает None.
	Иначе - возвращает обновленную запись согласно схеме. 
	"""	

	cursor.execute(
		'''
		UPDATE users SET bio = ? WHERE username = ?
		''',
		(update_data.bio, username)
	)
	
	return get_by_username(cursor=cursor, username=username)
