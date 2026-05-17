import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from starlette import status

from app.database import models
from app.security import decode_access_token, get_password_hash
from tests.conftest import create_john_user


@pytest.mark.parametrize(
    'data',
    (
        {
            'username': 'jane.doe',
            'password': 'password',
        },
        {
            'username': 'john.doe',
            'password': 'badpawword',
        },
    ),
)
def test_cannot_login_with_invalid_data(
    client: TestClient, session: Session, data: dict[str, str]
) -> None:
    create_john_user(session)
    r = client.post('/auth/login', data=data)
    assert r.status_code == status.HTTP_401_UNAUTHORIZED


def test_can_login(client: TestClient, session: Session) -> None:
    new_user = models.User(
        username='john.doe',
        password=get_password_hash('password'),
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    r = client.post(
        '/auth/login',
        data={
            'username': 'john.doe',
            'password': 'password',
        },
    )

    assert r.status_code == status.HTTP_200_OK

    response_data = r.json()
    assert 'access_token' in response_data

    username = decode_access_token(response_data['access_token'])
    assert username == new_user.username
