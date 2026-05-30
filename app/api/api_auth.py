from fastapi import APIRouter, status

from app import schema
from app.api.dependencies import CursorDatabase, OAuth2Form
from app.api.exceptions import ConflictHTTPException, LoginHTTPException
from app.services import auth_service, users_service

auth_router = APIRouter(prefix='/auth', tags=['Аккаунты'])


@auth_router.post(
	'/',
	summary='Регистрация',
	status_code=201,
	responses={
		status.HTTP_409_CONFLICT: {'description': 'Выбранный юзернейм занят'},
		status.HTTP_422_UNPROCESSABLE_CONTENT: {'description': 'Данные не валидны'},
	},
)
def register(
	cursor: CursorDatabase,
	new_user_payload: schema.UserCreate,
) -> None:
	existing_user = users_service.get_by_username(cursor=cursor, username=new_user_payload.username)

	if existing_user is not None:
		raise ConflictHTTPException(detail='Выбранный юзернейм занят')

	auth_service.register(cursor=cursor, user_data=new_user_payload)


@auth_router.post(
	'/login',
	summary='Логин',
	response_model=schema.UserToken,
	status_code=200,
	responses={
		status.HTTP_401_UNAUTHORIZED: {'description': 'Некорректное имя или пароль'},
		status.HTTP_422_UNPROCESSABLE_CONTENT: {'description': 'Данные не валидны'},
	},
)
def login(
	cursor: CursorDatabase,
	user_credentials: OAuth2Form,
) -> schema.UserToken:
	user = users_service.get_by_username(cursor=cursor, username=user_credentials.username)

	if user is None:
		raise LoginHTTPException

	access_token = auth_service.authenticate(cursor=cursor, user_data=user_credentials)

	if access_token is None:
		raise LoginHTTPException

	return schema.UserToken(access_token=access_token)
