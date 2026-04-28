import sqlite3
from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt import InvalidTokenError
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import security, schema
from app.api.exceptions import CredentialsHTTPException, NotFoundHTTPException
from app.database import SessionLocal, get_sqlite3_connection, models
from app.services import users_service


oauth2 = OAuth2PasswordBearer(tokenUrl='/auth/login')
TokenDependency = Annotated[str, Depends(oauth2)]
OAuth2Form = Annotated[OAuth2PasswordRequestForm, Depends()]


def _get_db_sa() -> Generator[Session]:
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()


def _get_db_sqlite() -> Generator[sqlite3.Cursor]:
	connection = get_sqlite3_connection()
	cursor = connection.cursor()
	try:
		yield cursor
		connection.commit()
	except sqlite3.DatabaseError:
		connection.rollback()
	finally:
		connection.close()


CursorDatabase = Annotated[sqlite3.Cursor, Depends(_get_db_sqlite)]
SessionDatabase = Annotated[Session, Depends(_get_db_sa)]


def _get_current_user(
	cursor: CursorDatabase,
	token: TokenDependency,
) -> schema.UserProfile:
	try:
		username = security.decode_access_token(token)
		user = users_service.get_by_username(cursor=cursor, username=username)
		if not user:
			raise NotFoundHTTPException(detail='Пользователь не найден')
		return user
	except (InvalidTokenError, ValidationError, KeyError):
		raise CredentialsHTTPException


CurrentUser = Annotated[schema.UserProfile, Depends(_get_current_user)]
