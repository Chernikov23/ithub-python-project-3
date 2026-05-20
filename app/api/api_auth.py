from fastapi import APIRouter, status

from app import schema
from app.api.dependencies import CurrentUser, CursorDatabase, OAuth2Form
from app.api.exceptions import (
	ConflictHTTPException,
	CredentialsHTTPException,
	LoginHTTPException,
)
from app.services import auth_service, users_service

# Роутер должен быть определен до того, как мы используем @auth_router
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
	existing = users_service.get_by_username(cursor=cursor, username=new_user_payload.username)
	if existing:
		raise ConflictHTTPException(detail='Выбранный юзернейм занят')
	try:
		auth_service.register(cursor=cursor, user_data=new_user_payload)
	except Exception as e:
		raise ConflictHTTPException(detail=str(e))


@auth_router.post(
	'/login',
	summary='Логин',
	response_model=schema.UserToken,
	status_code=200,  # Для тестов нужно 200
	responses={
		status.HTTP_401_UNAUTHORIZED: {'description': 'Некорректное имя или пароль'},
		status.HTTP_422_UNPROCESSABLE_CONTENT: {'description': 'Данные не валидны'},
	},
)
def login(
	cursor: CursorDatabase,
	user_credentials: OAuth2Form,
) -> schema.UserToken:
	user_data = schema.UserCreate(
		username=user_credentials.username, password=user_credentials.password
	)
	exists = users_service.get_by_username(cursor=cursor, username=user_data.username)
	if not exists:
		raise LoginHTTPException()

	token = auth_service.authenticate(cursor=cursor, user_data=user_data)
	if token is None:
		raise LoginHTTPException()
	return schema.UserToken(access_token=token)


@auth_router.get(
	'/me',
	summary='Информация о текущем залогиненном пользователе',
	response_model=schema.UserProfile,
	responses={
		status.HTTP_401_UNAUTHORIZED: {'description': 'Ошибка токена или пользовательских данных'},
	},
)
def get_current(
	current_user: CurrentUser,
) -> schema.UserProfile:
	if not current_user:
		raise CredentialsHTTPException()
	return current_user
