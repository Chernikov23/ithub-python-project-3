from sqlalchemy import select
from sqlalchemy.orm import Session

from app import schema
from app.database import models


def get_by_username(*, session: Session, username: str) -> models.User | None:
	return session.scalar(select(models.User).filter_by(username=username))


def update(*, session: Session, db_obj: models.User, obj_in: schema.UserUpdate) -> models.User:
	db_obj = session.merge(db_obj)

	db_obj.username = db_obj.username
	db_obj.bio = obj_in.bio or db_obj.bio

	session.add(db_obj)
	session.commit()
	session.refresh(db_obj)

	return db_obj
