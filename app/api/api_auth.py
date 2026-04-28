from fastapi import APIRouter, status

from app import schema
from app.api.exceptions import ConflictHTTPException, LoginHTTPException
from app.api.dependencies import OAuth2Form, SessionDatabase
from app.services import auth_service, users_service

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

	raise NotImplementedError


@auth_router.post(
	'/login',
	summary='Логин',
	response_model=schema.UserToken,
	status_code=201,
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

	raise NotImplementedError
