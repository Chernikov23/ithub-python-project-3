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
	
	user = cursor.execute('SELECT username, role, bio FROM users WHERE username = ?;', (username,)).fetchone()

	if not user:
		return None
	
	return schema.UserProfile(username=user[0], role=user[1], bio=user[2])


def update(*, cursor: Cursor, username: str, update_data: schema.UserUpdate) -> schema.UserProfile | None:
	"""
	:cursor: курсор подключения к базе данных
	:username: уникальный юзернейм пользователя
	:update_data: данные для обновления
	
	Запрашивает пользователя из базы данных. 
	Если пользователь не найден, возвращает None.
	Иначе - возвращает обновленную запись согласно схеме. 
	"""	

	
	updated = cursor.execute('UPDATE users SET bio = ? WHERE username = ?;',
				(update_data.bio, username)).rowcount > 0
	
	if updated:
		cursor.connection.commit()
	
	return schema.UserProfile(username=username, bio=update_data.bio) if updated else None