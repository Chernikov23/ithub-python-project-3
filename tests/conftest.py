import os

os.environ['PYTHON_ENVIRONMENT'] = 'testing'

import sqlite3
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete, create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.exc import IntegrityError

from app.config import settings
from app.security import create_access_token
from app.database import Base, models
from app.main import app

engine = create_engine(settings.DATABASE_URI, pool_pre_ping=True)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope='function')
def session() -> Generator:
	with TestingSessionLocal() as session:
		Base.metadata.create_all(bind=engine)

		yield session

		session.execute(delete(models.Dream))
		session.execute(delete(models.User))
		session.commit()


@pytest.fixture(scope='function')
def client() -> Generator:
	yield TestClient(app)


def create_john_user(session: Session) -> models.User | None:
	john_object = models.User(
		username='john.doe',
		password='john.doe.password',
	)
	try:
		session.add(john_object)
		session.commit()
		session.refresh(john_object)
		return john_object
	except (IntegrityError, sqlite3.IntegrityError):
		session.rollback()
		return session.scalar(select(models.User).where(models.User.username == john_object.username))
	finally:
		session.close()


def create_jane_user(session: Session) -> models.User | None:
	jane_object = models.User(
		username='jane.doe',
		password='jane.doe.password',
	)
	try:
		session.add(jane_object)
		session.commit()
		session.refresh(jane_object)
		return jane_object
	except (IntegrityError, sqlite3.IntegrityError):
		session.rollback()
		return session.scalar(select(models.User).where(models.User.username == jane_object.username))
	finally:
		session.close()


def acting_as_guest(client: TestClient) -> None:
	if client.headers.get('Authorization'):
		del client.headers['Authorization']


def acting_as_user(user: models.User, client: TestClient) -> models.User:
	token = create_access_token(user.username)
	client.headers['Authorization'] = f'Bearer {token}'
	return user


def acting_as_john(session: Session, client: TestClient) -> models.User:
	user = create_john_user(session)
	assert user is not None
	return acting_as_user(user, client)


def acting_as_jane(session: Session, client: TestClient) -> models.User:
	user = create_jane_user(session)
	assert user is not None
	return acting_as_user(user, client)


def generate_dream(author: models.User, id: int | None = None) -> models.Dream:
	return models.Dream(
		description=f'Test Description {id}',
		id=id,
		author=author,
	)


def generate_dreams(session: Session) -> models.User:
	john = create_john_user(session)
	jane = create_jane_user(session)

	assert john is not None
	assert jane is not None


	for i in range(1, 21):
		dream = models.Dream(
			description=f'Test Description {i}',
			id=i,
			author=john,
		)
		session.add(dream)
		session.commit()

	for i in range(21, 41):
		dream = models.Dream(
			description=f'Test Description {i}',
			id=i,
			author=jane,
		)

		session.add(dream)
		session.commit()

	session.refresh(john)
	
	# session.close()
	return john
