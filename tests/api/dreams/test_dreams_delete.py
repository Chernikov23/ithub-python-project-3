from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session
from starlette import status

from app.database import models
from tests.conftest import (
	acting_as_admin,
	acting_as_guest,
	acting_as_john,
	create_jane_user,
	generate_dream,
)


def test_guest_cannot_delete_dream(client: TestClient, session: Session) -> None:
	john = acting_as_john(session, client)

	john_dream = generate_dream(john, id=1)
	session.add(john_dream)
	session.commit()
	session.close()

	acting_as_guest(client)
	r = client.delete('/dreams/1')

	assert r.status_code == status.HTTP_401_UNAUTHORIZED


def test_superadmin_can_delete_dreams(client: TestClient, session: Session) -> None:
	jane = create_jane_user(session)
	assert jane is not None

	jane_dream = generate_dream(author=jane, id=1)
	session.add(jane_dream)
	session.commit()

	acting_as_admin(session, client)
	r = client.delete('/dreams/1')

	assert r.status_code == status.HTTP_204_NO_CONTENT
	assert session.scalar(select(models.Dream)) is None


def test_cannot_delete_non_existent_dream(client: TestClient, session: Session) -> None:
	acting_as_john(session, client)
	r = client.delete('/dreams/50')
	assert r.status_code == status.HTTP_404_NOT_FOUND


def test_cannot_delete_dream_of_other_author(client: TestClient, session: Session) -> None:
	jane = create_jane_user(session)

	assert jane is not None

	jane_dream = generate_dream(author=jane)
	session.add(jane_dream)
	session.commit()

	acting_as_john(session, client)
	r = client.delete('/dreams/1')

	assert r.status_code == status.HTTP_403_FORBIDDEN


def test_can_delete_own_dream(client: TestClient, session: Session) -> None:
	john = acting_as_john(session, client)

	john_dream = generate_dream(john)
	session.add(john_dream)
	session.commit()

	r = client.delete('/dreams/1')

	assert r.status_code == status.HTTP_204_NO_CONTENT
	assert session.scalar(select(models.Dream)) is None
