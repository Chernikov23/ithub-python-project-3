from sqlite3 import Cursor
from app import schema


def get_by_username(*, cursor: Cursor, username: str) -> schema.UserProfile | None:
	cursor.execute(
		'SELECT username FROM users WHERE username = ?',
		(username,),
	)

	user = cursor.fetchone()

	if user is None:
		return None

	return schema.UserProfile(username=user[0])

	raise NotImplemented
