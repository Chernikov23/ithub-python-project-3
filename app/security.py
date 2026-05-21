import hashlib
from datetime import datetime, timedelta
from jose import jwt, JWTError
from app.config import settings

ALGORITHM = settings.JWT_ALGORITHM

def hash_password(plain_password: str) -> str:
    salt = settings.PASSWORD_SALT.encode() if isinstance(settings.PASSWORD_SALT, str) else settings.PASSWORD_SALT
    derived = hashlib.pbkdf2_hmac('sha256', plain_password.encode(), salt, 100000)
    return derived.hex()

get_password_hash = hash_password

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return hash_password(plain_password) == hashed_password

def create_access_token(username: str) -> str:
    to_encode = {"sub": username, "exp": datetime.utcnow() + timedelta(seconds=settings.JWT_EXPIRE)}
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> str:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[ALGORITHM])
        username: str | None = payload.get("sub")
        if username is None:
            raise ValueError()
        return username
    except (JWTError, ValueError):
        raise ValueError("Invalid token")