import sqlite3

from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings


class Base(DeclarativeBase):
	pass


def _db_path() -> str:
	return settings.DATABASE_URI.removeprefix('sqlite:///')


def get_sqlite3_connection() -> sqlite3.Connection:
	conn = sqlite3.connect(
		_db_path(),
		check_same_thread=False,
		timeout=15,
	)
	conn.execute('PRAGMA busy_timeout = 15000')
	conn.execute('PRAGMA journal_mode = WAL')
	return conn


engine = create_engine(
	settings.DATABASE_URI,
	pool_pre_ping=True,
	connect_args={'check_same_thread': False, 'timeout': 15},
)


@event.listens_for(engine, 'connect')
def _set_sqlite_pragma(dbapi_connection, connection_record):
	cursor = dbapi_connection.cursor()
	cursor.execute('PRAGMA busy_timeout = 15000')
	cursor.execute('PRAGMA journal_mode = WAL')
	cursor.close()


SessionLocal = sessionmaker(autoflush=False, bind=engine)
