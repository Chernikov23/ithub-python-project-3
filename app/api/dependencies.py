from collections.abc import Generator
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt import InvalidTokenError
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import security
from app.api.exceptions import CredentialsHTTPException
from app.database import SessionLocal, models
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
		user = session.scalar(select(models.User).filter_by(username=username))

		if not user:
			raise HTTPException(status_code=401, detail='Пользователь не найден')
		return user
	except (InvalidTokenError, ValidationError, KeyError):
		raise CredentialsHTTPException


CurrentUser = Annotated[models.User, Depends(_get_current_user)]
