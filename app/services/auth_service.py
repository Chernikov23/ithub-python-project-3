from sqlalchemy.orm import Session

from app import schema
from app.database import exceptions, models
from app.security import create_access_token, get_password_hash, verify_password


def register(*, session: Session, obj_in: schema.UserCreate) -> models.User:
	db_obj = models.User(
		username=obj_in.username,
		password=get_password_hash(obj_in.password),
	)
	session.add(db_obj)
	session.commit()
	session.refresh(db_obj)
	return db_obj


def authenticate(*, found_user: models.User, password: str) -> str:
	if not found_user.password:
		raise exceptions.LoginHTTPException

	if not verify_password(password, found_user.password):
		raise exceptions.LoginHTTPException

	return create_access_token(found_user.username)
