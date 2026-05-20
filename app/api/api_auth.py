from fastapi import APIRouter, status

from app import schema
from app.api.exceptions import ConflictHTTPException, LoginHTTPException
from app.api.dependencies import OAuth2Form, CurrentUser, SessionDatabase
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
	session: SessionDatabase,
	new_user_payload: schema.UserCreate,
) -> None:
	existing = users_service.get_by_username(session=session, username=new_user_payload.username)
	if existing:
		raise ConflictHTTPException(detail="имя занято")
	
	auth_service.register(session=session, user_data=new_user_payload)


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
	session: SessionDatabase,
	user_credentials: OAuth2Form,
) -> schema.UserToken:
	user = users_service.get_by_username(
		session=session,
		username=user_credentials.username
	)
	if user is None:
		raise LoginHTTPException()
	
	token = auth_service.authenticate(
		session=session,
		user_data=schema.UserCreate(
			username=user_credentials.username,
			password=user_credentials.password
		)
	)

	if token is None:
		raise LoginHTTPException()

	return schema.UserToken(
		access_token=token,
		token_type="bearer"
	)


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
	return current_user
