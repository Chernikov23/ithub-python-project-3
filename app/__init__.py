import sqlite3
from typing import Any

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.database import models
from app.config import settings


class Base(DeclarativeBase):
	pass


def get_sqlite3_connection() -> sqlite3.Connection:
	connection = sqlite3.connect(
		settings.DATABASE_URI.lstrip('sqlite:///'),
		autocommit=False,
		check_same_thread=False,
	)
	connection.execute('PRAGMA busy_timeout=5000')
	return connection


engine = create_engine(settings.DATABASE_URI.__str__(), pool_pre_ping=True)
SessionLocal = sessionmaker(autoflush=False, bind=engine)


@event.listens_for(Engine, 'connect')
def _set_sqlite_pragmas(dbapi_connection: Any, connection_record: Any) -> None:
	cursor = dbapi_connection.cursor()
	cursor.execute('PRAGMA journal_mode=WAL')
	cursor.execute('PRAGMA busy_timeout=5000')
	cursor.close()


def init_database() -> None:

	Base.metadata.create_all(bind=engine)


init_database()
