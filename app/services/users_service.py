from sqlite3 import Cursor

from app import schema


def get_by_username(*, cursor: Cursor, username: str) -> schema.UserProfile | None:
	"""
	Возвращает UserProfile или None.
	"""
	cursor.execute('SELECT username FROM users WHERE username = ?', (username,))
	row = cursor.fetchone()
	if not row:
		return None
	return schema.UserProfile(username=row[0])
