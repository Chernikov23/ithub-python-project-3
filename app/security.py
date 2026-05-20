from datetime import UTC, datetime, timedelta

import jwt
from pwdlib import PasswordHash

from app.config import settings


def create_access_token(subject: str) -> str:
	expire = datetime.now(UTC) + timedelta(minutes=settings.JWT_EXPIRE)
	to_encode = {'exp': expire, 'sub': subject}
	return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> str:
	token_data = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
	return token_data['sub']


def verify_password(plain_password: str, hashed_password: str) -> bool:
	return password_hasher.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
	return password_hasher.hash(password, salt=settings.PASSWORD_SALT)


password_hasher = PasswordHash.recommended()
