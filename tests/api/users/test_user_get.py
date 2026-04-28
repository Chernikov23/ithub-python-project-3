from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from starlette import status

from tests.conftest import create_john_user


def test_cannot_get_non_existent_profile(client: TestClient) -> None:
	r = client.get('/users/john.doe')

	assert r.status_code == status.HTTP_404_NOT_FOUND


def test_can_get_user(client: TestClient, session: Session) -> None:
	create_john_user(session)

	r = client.get('/users/john.doe')

	assert r.status_code == status.HTTP_200_OK

	assert r.json() == {'username': 'john.doe'}
