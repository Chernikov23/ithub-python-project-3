from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from starlette import status

from tests.conftest import acting_as_john


def test_guest_cannot_fetch_infos(client: TestClient) -> None:
    r = client.get('/auth/me')

    assert r.status_code == status.HTTP_401_UNAUTHORIZED


def test_user_can_fetch_infos(client: TestClient, session: Session) -> None:
    acting_as_john(session, client)

    r = client.get('/auth/me')

    assert r.status_code == status.HTTP_200_OK
    assert r.json()['username'] == 'john.doe'
