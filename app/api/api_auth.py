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
	existing_user = users_service.get_by_username(session=session, username=new_user.username)

	if existing_user:
		raise ConflictHTTPException('Выбранный юзернейм занят')

	try:
		auth_service.register(session=session, obj_in=new_user)
	except Exception:
		raise HTTPException(status_code=400)


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
	user = users_service.get_by_username(session=session, username=user_credentials.username)

	if not user:
		raise LoginHTTPException

	access_token = auth_service.authenticate(found_user=user, password=user_credentials.password)

	return schema.UserToken(access_token=access_token, token_type='bearer')
