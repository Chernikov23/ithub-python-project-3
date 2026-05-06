from fastapi.testclient import TestClient
from sqlalchemy import select, text
from sqlalchemy.orm import Session
from starlette import status

from app.database import models
from tests.conftest import acting_as_john, create_jane_user, generate_dream, acting_as_guest


def test_guest_cannot_favorite_dream(client: TestClient, session: Session) -> None:
	john = acting_as_john(session, client)

	john_dream = generate_dream(john, id=1)
	session.add(john_dream)
	session.commit()
	session.close()

	acting_as_guest(client)
	r = client.post('/dreams/1/favorite')

	assert r.status_code == status.HTTP_401_UNAUTHORIZED


def test_cannot_favorite_non_existent_dream(client: TestClient, session: Session) -> None:
	acting_as_john(session, client)
	r = client.post('/dreams/50/favorite')
	assert r.status_code == status.HTTP_404_NOT_FOUND


def test_can_favorite_dream(client: TestClient, session: Session) -> None:
	john = acting_as_john(session, client)

	john_dream = generate_dream(john, id=1)
	session.add(john_dream)
	session.commit()
	session.close()

	r = client.post('/dreams/1/favorite')

	assert r.status_code == status.HTTP_200_OK

	assert {
		'description': 'Test Description 1',
		'favorited_by': ['john.doe'],
		'favorites_count': 1,
	}.items() <= r.json().items()

	assert session.scalar(select(models.dream_favorite)) is not None


def test_can_unfavorite_dream(client: TestClient, session: Session) -> None:
	jane = create_jane_user(session)
	john = acting_as_john(session, client)

	assert jane is not None
	assert john is not None

	jane_dream = generate_dream(jane, id=1)
	session.add(jane_dream)
	session.commit()

	session.execute(
		text('INSERT INTO dream_favorite (username, dream_id) VALUES (:username, :dream_id)'),
		{'username': 'john.doe', 'dream_id': jane_dream.id}
	)
	session.commit()

	r = client.delete('/dreams/1/favorite')

	assert r.status_code == status.HTTP_200_OK
	
	json_response = r.json()

	assert json_response["description"] == 'Test Description 1'
	assert json_response["favorited_by"] == []
	assert json_response["favorites_count"] == 0

	assert session.scalar(select(models.dream_favorite)) is None
