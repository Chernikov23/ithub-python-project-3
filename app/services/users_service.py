from sqlite3 import Cursor

from app import schema


def get_by_username(*, cursor: Cursor, username: str) -> schema.UserProfile | None:
	row = cursor.execute(
		'SELECT username, bio, is_superuser FROM users WHERE username = ?',
		(username,),
	).fetchone()

	if row is None:
		return None

	return schema.UserProfile(username=row[0], bio=row[1], is_superuser=bool(row[2]))


def update(
	*, cursor: Cursor, username: str, update_data: schema.UserUpdate
) -> schema.UserProfile | None:
	row = cursor.execute(
		'SELECT username FROM users WHERE username = ?',
		(username,),
	).fetchone()

	if row is None:
		return None

	cursor.execute(
		'UPDATE users SET bio = ? WHERE username = ?',
		(update_data.bio, username),
	)

	updated = cursor.execute(
		'SELECT username, bio, is_superuser FROM users WHERE username = ?',
		(username,),
	).fetchone()

	return schema.UserProfile(username=updated[0], bio=updated[1], is_superuser=bool(updated[2]))
