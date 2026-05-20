from sqlalchemy import select
from sqlalchemy.orm import Session
from app import schema
from app.database import models

def get_by_username(*, session: Session, username: str) -> schema.UserProfile | None:
	user = session.execute(
		select(models.User).where(models.User.username == username)
	).unique().scalar_one_or_none()
	
	if user:
		return schema.UserProfile(username=user.username)
	return None

def get_user_with_password(*, session: Session, username: str) -> tuple[str, str] | None:
	user = session.execute(
		select(models.User).where(models.User.username == username)
	).unique().scalar_one_or_none()
	
	if user:
		return (user.username, user.password)
	return None