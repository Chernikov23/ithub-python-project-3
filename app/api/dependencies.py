import sqlite3
from collections.abc import Generator
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import schema, security
from app.api.exceptions import CredentialsHTTPException, NotFoundHTTPException
from app.database import SessionLocal, get_sqlite3_connection, models
from app.services import users_service

oauth2 = OAuth2PasswordBearer(tokenUrl='/auth/login')

OAuth2Form = Annotated[OAuth2PasswordRequestForm, Depends()]
TokenDependency = Annotated[str, Depends(oauth2)]

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def _get_db_sqlite() -> Generator[sqlite3.Cursor, None, None]:
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
SessionDatabase = Annotated[Session, Depends(get_db)]

def get_current_user(
    cursor: CursorDatabase,
    token: TokenDependency,
) -> schema.UserProfile:
    try:
        username = security.decode_access_token(token)
        user = users_service.get_by_username(cursor=cursor, username=username)
        if not user:
            raise CredentialsHTTPException()
        return user
    except Exception:
        raise CredentialsHTTPException()

CurrentUser = Annotated[schema.UserProfile, Depends(get_current_user)]

def get_current_active_user(
    current_user: CurrentUser,
    session: SessionDatabase,
) -> models.User:
    user = session.query(models.User).filter(models.User.username == current_user.username).first()
    if not user:
        raise CredentialsHTTPException()
    return user