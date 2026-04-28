from fastapi import APIRouter, HTTPException

from app import schema
from app.api.exceptions import ConflictHTTPException, LoginHTTPException
from app.api.dependencies import OAuth2Form, SessionDatabase
from app.services import auth_service, users_service

auth_router = APIRouter(prefix='/auth', tags=['Аккаунты'])


@auth_router.post('/', summary='Регистрация', status_code=201)
def register(
	session: SessionDatabase,
	new_user: schema.UserCreate,
) -> None:
	pass


@auth_router.post(
	'/login',
	summary='Логин',
	response_model=schema.UserToken,
	status_code=201
)
def login(
	session: SessionDatabase,
	user_credentials: OAuth2Form,
) -> schema.UserToken:
	pass