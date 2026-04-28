from sqlalchemy.orm import Session

from app import schema
from app.api.exceptions import LoginHTTPException
from app.database import models
from app.security import create_access_token, get_password_hash, verify_password


def register(*, session: Session, obj_in: schema.UserCreate) -> models.User:
	pass


def authenticate(*, found_user: models.User, password: str) -> str:
	pass