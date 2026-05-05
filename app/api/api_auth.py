from fastapi import APIRouter, status

from app import schema
from app.api.dependencies import OAuth2Form, SessionDatabase
from app.services.users_service import get_by_username
import app.services.auth_service as authsvc
from app.api.exceptions import *
from sqlite3 import Cursor

auth_router = APIRouter(prefix='/auth', tags=['Аккаунты'])


@auth_router.post(
		'/', 
		summary='Регистрация', 
		status_code=201,
		responses={
			status.HTTP_409_CONFLICT: { "description": "Выбранный юзернейм занят" },
			status.HTTP_422_UNPROCESSABLE_CONTENT: { "description": "Данные не валидны" }
		},
)
def register(
	session: SessionDatabase,
	new_user_payload: schema.UserCreate,
) -> None:
	"""
	Запрашивает users_service на предмет наличия пользователя с переданным именем.
	Если пользователь найден, выбрасывает ConflictHTTPException с пояснением.
	Иначе - проводит регистрацию через auth_service. 
	"""

	cursor = session.get_bind().raw_connection().cursor()

	if get_by_username(cursor=cursor, username=new_user_payload.username):
		raise ConflictHTTPException('Выбранный юзернейм занят')

	authsvc.register(cursor=cursor, user_data=new_user_payload)


@auth_router.post(
	'/login',
	summary='Логин',
	response_model=schema.UserToken,
	status_code=200,
	responses={
		status.HTTP_401_UNAUTHORIZED: { "description": "Некорректное имя или пароль" },
		status.HTTP_422_UNPROCESSABLE_CONTENT: { "description": "Данные не валидны" }
	}
)
def login(
	session: SessionDatabase,
	user_credentials: OAuth2Form,
) -> schema.UserToken:
	"""
	Запрашивает users_service на предмет наличия пользователя с переданным именем.
	Если пользователь не найден, выбрасывает LoginHTTPException с пояснением.
	Иначе - запрашивает аутентификацию через auth_service. Если пароль некорректен,
	выбрасывает LoginHTTPException с пояснением. Иначе - возвращает токен согласно схеме.
	"""

	cursor: Cursor = session.get_bind().raw_connection().cursor()

	user = get_by_username(cursor=cursor, username=user_credentials.username)

	if not user:
		raise LoginHTTPException()
	
	token = authsvc.authenticate(cursor=cursor, user_data=schema.UserCreate(username=user.username,
																		 password=user_credentials.password,
																		 role=user.role))
	
	if not token:
		raise LoginHTTPException()

	return schema.UserToken(access_token=token)