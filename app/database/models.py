from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Table, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base, engine

dream_favorite: Table = Table(
	'dream_favorite',
	Base.metadata,
	Column(
		'dream_id',
		Integer,
		ForeignKey('dreams.id', ondelete='CASCADE'),
		primary_key=True,
	),
	Column('username', String, ForeignKey('users.username', ondelete='CASCADE'), primary_key=True),
)


class Dream(Base):
	__tablename__ = 'dreams'

	id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
	author: Mapped[str] = mapped_column(String, ForeignKey('users.username'), nullable=False)
	description: Mapped[str] = mapped_column(Text, nullable=False)
	created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)

	__table_args__ = (UniqueConstraint('author', 'description', name='uq_author_description'),)


class User(Base):
	__tablename__ = 'users'

	username: Mapped[str] = mapped_column(String, primary_key=True, index=True)
	password: Mapped[str] = mapped_column(String, nullable=False)
	bio: Mapped[str | None] = mapped_column(Text, nullable=True)
	role: Mapped[str] = mapped_column(String, nullable=False, default='user')