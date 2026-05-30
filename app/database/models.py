from datetime import datetime

from sqlalchemy import (
	Boolean,
	Column,
	DateTime,
	ForeignKey,
	Integer,
	String,
	Table,
	Text,
	UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

dream_favorite: Table = Table(
	'dream_favorite',
	Base.metadata,
	Column(
		'dream_id',
		Integer,
		ForeignKey('dreams.id', ondelete='CASCADE'),
		primary_key=True,
	),
	Column('user_id', String, ForeignKey('users.username', ondelete='CASCADE'), primary_key=True),
)


class Dream(Base):
	__tablename__ = 'dreams'

	id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
	author_id: Mapped[str] = mapped_column(String, ForeignKey('users.username'), nullable=False)
	description: Mapped[str] = mapped_column(Text, nullable=False)
	created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)

	author: Mapped['User'] = relationship('User', back_populates='dreams', lazy='joined')
	favorited_by: Mapped[list['User']] = relationship(
		'User',
		back_populates='favorite_dreams',
		secondary=dream_favorite,
		uselist=True,
		lazy='joined',
	)

	__table_args__ = (UniqueConstraint('author_id', 'description', name='uq_author_description'),)


class User(Base):
	__tablename__ = 'users'

	username: Mapped[str] = mapped_column(String, primary_key=True, index=True)
	password: Mapped[str | None] = mapped_column(String, nullable=False)
	bio: Mapped[str | None] = mapped_column(Text, nullable=True)
	is_superuser: Mapped[bool] = mapped_column(
		Boolean, default=False, server_default='0', nullable=False
	)

	dreams: Mapped[list[Dream]] = relationship('Dream', back_populates='author', lazy='joined')
	favorite_dreams: Mapped[list[Dream]] = relationship(
		'Dream',
		back_populates='favorited_by',
		secondary=dream_favorite,
		lazy='joined',
	)
