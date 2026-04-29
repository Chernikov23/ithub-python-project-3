import sqlite3
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from starlette import status

from tests.conftest import acting_as_user, generate_dreams


def test_can_paginate_dreams(client: TestClient, session: Session) -> None:
	generate_dreams(session)

	r = client.get('/dreams?limit=10&offset=20')

	assert r.status_code == status.HTTP_200_OK

	json_response = r.json() 

	assert len(json_response['dreams']) == 10
	assert json_response['dreams_count'] == 40

	json_response['dreams'][0].pop('created_at')

	assert {
		'id': 20,
		'description': 'Test Description 20',
		'author': {
			'username': 'john.doe',
			'bio': None,
		},
		'favorited_by': [],
		'favorites_count': 0,
	} == json_response['dreams'][0]


def test_can_filter_dreams_by_author(client: TestClient, session: Session) -> None:
	generate_dreams(session)

	r = client.get('/dreams?limit=10&offset=0&author=john')

	assert r.status_code == status.HTTP_200_OK

	json_response = r.json() 

	assert len(json_response['dreams']) == 10
	assert json_response['dreams_count'] == 20

	json_response['dreams'][0].pop('created_at')

	assert {
		'id': 20,
		'description': 'Test Description 20',
		'author': {
			'username': 'john.doe',
			'bio': None,
		},
		'favorited_by': [],
		'favorites_count': 0,
	} == dict(json_response['dreams'][0])


def test_can_filter_dreams_by_favorited(client: TestClient, session: Session) -> None:
	john = generate_dreams(session)
	acting_as_user(john, client)

	r = client.get('/dreams?limit=10&offset=0&favorited=john')

	assert r.status_code == status.HTTP_200_OK

	json_response = r.json() 

	assert len(json_response['dreams']) == 5
	assert json_response['dreams_count'] == 5

	json_response['dreams'][0].pop('created_at')

	assert {
		'id': 29,
		'description': 'Test Description 29',
		'author': {
			'username': 'jane.doe',
			'bio': None,
		},
		'favorited_by': ['john.doe'],
		'favorites_count': 1,
	} == json_response['dreams'][0]