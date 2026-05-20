import hashlib
from datetime import datetime, timedelta

from jose import jwt

from app.config import settings

ALGORITHM = settings.JWT_ALGORITHM


def hash_password(plain_password: str) -> str:
	derived = hashlib.pbkdf2_hmac(
		'sha256',
		plain_password.encode(),
		settings.PASSWORD_SALT.encode()
		if isinstance(settings.PASSWORD_SALT, str)
		else settings.PASSWORD_SALT,
		100000,
	)
	return derived.hex()


def verify_password(plain_password: str, hashed_password: str) -> bool:
	try:
		salt = (
			settings.PASSWORD_SALT.encode()
			if isinstance(settings.PASSWORD_SALT, str)
			else settings.PASSWORD_SALT
		)
		derived = hashlib.pbkdf2_hmac(
			'sha256',
			plain_password.encode(),
			salt,
			100000,
		)
		return derived.hex() == hashed_password
	except Exception:
		return False


def create_access_token(data: dict) -> str:
	to_encode = data.copy()
	expire = datetime.utcnow() + timedelta(seconds=settings.JWT_EXPIRE)
	to_encode.update({'exp': expire})
	encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
	return encoded_jwt
