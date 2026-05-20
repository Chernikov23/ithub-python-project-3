from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
	# Указываем значения по умолчанию, чтобы не было ошибки "Field required"
	DATABASE_URI: str = 'sqlite:///./app/database/local.sqlite3'
	PASSWORD_SALT: str = 'super_secret_salt_change_me'
	JWT_SECRET_KEY: str = 'another_secret_key_for_jwt'
	JWT_ALGORITHM: str = 'HS256'
	JWT_EXPIRE: int = 3600
	DEBUG: bool = False

	model_config = SettingsConfigDict(
		env_file='.env',
		extra='ignore',
	)


settings: Settings = Settings()
