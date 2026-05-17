from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from starlette import status

from tests.conftest import acting_as_john, generate_dream


def test_cannot_get_non_existent_dream(client: TestClient) -> None:
    r = client.get('/dreams/1')
    assert r.status_code == status.HTTP_404_NOT_FOUND


def test_can_get_dream(client: TestClient, session: Session) -> None:
    john = acting_as_john(session, client)

    db_obj = generate_dream(john, id=1)
    session.add(db_obj)
    session.commit()

    r = client.get('/dreams/1')

    assert r.status_code == status.HTTP_200_OK

    json_response = r.json()
    del json_response['created_at']

    assert {
        'id': 1,
        'description': 'Test Description 1',
        'author': 'john.doe',
    } == dict(json_response)
