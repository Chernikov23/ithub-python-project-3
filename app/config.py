from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URI: str = "sqlite:///./app/database/local.sqlite3"
    PASSWORD_SALT: str = "super_secret_salt"
    JWT_SECRET_KEY: str = "jwt_secret_key"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE: int = 3600
    DEBUG: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        extra='ignore',
    )

settings = Settings()