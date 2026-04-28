from collections.abc import Generator
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt import InvalidTokenError
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app import security
from app.database import SessionLocal, exceptions, models
from app.services import users_service

oauth2 = OAuth2PasswordBearer(tokenUrl='/auth/login')
TokenDependency = Annotated[str, Depends(oauth2)]
OAuth2Form = Annotated[OAuth2PasswordRequestForm, Depends()]


def _get_db() -> Generator:
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()


SessionDatabase = Annotated[Session, Depends(_get_db)]


def _get_current_user(
	session: SessionDatabase,
	token: TokenDependency,
) -> models.User:
	try:
		username = security.decode_access_token(token)
		user = users_service.get_by_username(session=session, username=username)
		if not user:
			raise HTTPException(status_code=401, detail='Пользователь не найден')
		return user
	except (InvalidTokenError, ValidationError, KeyError):
		raise exceptions.CredentialsHTTPException


CurrentUser = Annotated[models.User, Depends(_get_current_user)]
