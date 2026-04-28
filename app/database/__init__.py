from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings


class Base(DeclarativeBase):
	pass


engine = create_engine(settings.DATABASE_URI.__str__(), pool_pre_ping=True)
SessionLocal = sessionmaker(autoflush=False, bind=engine)