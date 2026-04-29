import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session
from starlette import status

from app.database import models
from tests.conftest import acting_as_john, generate_dream


def test_guest_cannot_create_dream(client: TestClient) -> None:
	r = client.post('/dreams')
	assert r.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize(
	'data',
	(
		{'description': ''},
		{},
	),
)
def test_cannot_create_dream_with_invalid_data(
	client: TestClient, session: Session, data: dict[str, str]
) -> None:
	acting_as_john(session, client)
	r = client.post('/dreams', json=data)
	assert r.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_cannot_create_dream_with_same_description(client: TestClient, session: Session) -> None:
	john = acting_as_john(session, client)

	john_dream = generate_dream(author=john, id=1)
	session.add(john_dream)
	session.commit()

	r = client.post(
		'/dreams',
		json={
			'description': 'Test Description 1',
		},
	)

	assert r.status_code == status.HTTP_409_CONFLICT


def test_can_create_dream(client: TestClient, session: Session) -> None:
	acting_as_john(session, client)

	r = client.post(
		'/dreams',
		json={
			'description': 'Test Description 1',
		},
	)

	assert r.status_code == status.HTTP_201_CREATED

	json_response = r.json()
	json_response.pop('created_at')

	assert {
		'id': 1,
		'description': 'Test Description 1',
		'author': 'john.doe',
	} == json_response

	assert (
		session.scalar(select(models.Dream).filter_by(description='Test Description 1')) is not None
	)
