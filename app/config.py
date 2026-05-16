import os
import secrets
import typing

from pydantic_settings import BaseSettings, SettingsConfigDict

def get_database_uri():
	if os.getenv('PYTHON_ENVIRONMENT') == 'testing':
		return 'sqlite:///./app/database/testing.sqlite3'
	return 'sqlite:///./app/database/local.sqlite3'

class Settings(BaseSettings):
	DEBUG: bool = os.getenv('PYTHON_ENVIRONMENT') != 'testing'

	JWT_SECRET_KEY: str = os.getenv('JWT_SECRET_KEY', secrets.token_urlsafe(32))
	JWT_EXPIRE: int = 60 * 24 * 8 * 10
	JWT_ALGORITHM: typing.Literal['HS256'] = 'HS256'

	PASSWORD_SALT: bytes = os.getenv('PASSWORD_SALT', 'default_salt').encode() 

	model_config = SettingsConfigDict(
		env_file='.env',
		strict=True,
	)
	DATABASE_URI: str = get_database_uri()


settings = Settings()
