from sqlite3 import Cursor
from app import schema

from sqlalchemy.orm import Session
from app.database import models


def get_by_username(*, cursor: Cursor, username: str) -> schema.UserProfile | None:
	cursor.execute('SELECT username FROM users WHERE username = ?', (username,))
	row = cursor.fetchone()
	if not row:
		return None
	return schema.UserProfile(username=row[0])


def get_by_username_sa(*, session: Session, username: str) -> schema.UserProfile | None:
	user = session.get(models.User, username)
	if not user:
		return None
	return schema.UserProfile(username=user.username)
