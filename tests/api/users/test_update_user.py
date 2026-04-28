import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session
from starlette import status

from app.database import models
from tests.conftest import acting_as_john


def test_guest_cannot_update(client: TestClient) -> None:
	r = client.put('/users')

	assert r.status_code == status.HTTP_401_UNAUTHORIZED


def test_user_can_update(client: TestClient, session: Session) -> None:
	acting_as_john(session, client)

	r = client.put(
		'/users',
		json={
			'bio': 'My Bio',
		},
	)

	assert r.status_code == status.HTTP_200_OK

	response_data = r.json()

	assert response_data['username'] == 'john.doe'
	assert response_data['bio'] == 'My Bio'

	assert (session.scalar(select(models.User).filter_by(username='john.doe'))) is not None
