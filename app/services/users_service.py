from sqlite3 import Cursor

from app import schema


def get_by_username(*, cursor: Cursor, username: str) -> schema.UserProfile | None:

	cursor.execute('SELECT username FROM users WHERE username = ?', (username,))
	user_record = cursor.fetchone()

	if not user_record:
		return None

	return schema.UserProfile(username=user_record[0])
