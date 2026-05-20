import sqlite3
from typing import Any

from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import settings


class Base(DeclarativeBase):
	pass


def get_sqlite3_connection() -> sqlite3.Connection:
	conn = sqlite3.connect(
		settings.DATABASE_URI.lstrip('sqlite:///'), check_same_thread=False, timeout=60
	)
	return conn


engine = create_engine(
	settings.DATABASE_URI.__str__(),
	poolclass=StaticPool,
	connect_args={'check_same_thread': False, 'timeout': 60},
)


@event.listens_for(engine, 'connect')
def set_sqlite_pragma(dbapi_connection: sqlite3.Connection, connection_record: Any) -> None:
	cursor = dbapi_connection.cursor()
	cursor.execute('PRAGMA foreign_keys=ON')
	cursor.close()


SessionLocal = sessionmaker(autoflush=False, bind=engine)
