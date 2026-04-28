import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session
from starlette import status

from app.database import models
from tests.conftest import create_john_user


@pytest.mark.parametrize(
	'data',
	(
		{
			'username': 'john.doe',
		},
		{
			'username': 'john.doe',
			'password': 'pass',
		},
		{
			'username': '',
			'password': 'password',
		},
		{
			'username': 'john.doe',
			'password': '',
		},
	),
)
def test_cannot_register_with_invalid_data(client: TestClient, data: dict[str, str]) -> None:
	r = client.post('/auth', json=data)

	assert r.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_cannot_register_twice(client: TestClient, session: Session) -> None:
	create_john_user(session)

	r = client.post(
		'/auth',
		json={
			'username': 'john.doe',
			'password': 'password',
		},
	)

	assert r.status_code == status.HTTP_409_CONFLICT


def test_can_register(client: TestClient, session: Session) -> None:
	r = client.post(
		'/auth',
		json={
			'username': 'john.doe',
			'password': 'password',
		},
	)

	assert r.status_code == status.HTTP_201_CREATED
	assert (session.scalar(select(models.User).filter_by(username='john.doe'))) is not None
