from fastapi import APIRouter, status

from app import schema
from app.api.exceptions import ConflictHTTPException, LoginHTTPException, CredentialsHTTPException, NotFoundHTTPException
from app.api.dependencies import OAuth2Form, CurrentUser, CursorDatabase
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
		status.HTTP_401_UNAUTHORIZED: {'description': 'Некорректное имя или пароль'},
		status.HTTP_422_UNPROCESSABLE_CONTENT: {'description': 'Данные не валидны'},
	},
)
def login(
	cursor: CursorDatabase,
	user_credentials: OAuth2Form,
) -> schema.UserToken:
	"""
	Запрашивает users_service на предмет наличия пользователя с переданным именем.
	Если пользователь не найден, выбрасывает LoginHTTPException с пояснением.
	Иначе - запрашивает аутентификацию через auth_service. Если пароль некорректен,
	выбрасывает LoginHTTPException с пояснением. Иначе - возвращает токен согласно схеме.
	"""

	raise NotImplementedError


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
	"""
	Получает текущего пользователя через инъекцию зависимостей, в случае
	ошибки выбрасывает CredentialsHTTPException. Иначе - отвечает согласно схеме.
	"""

	raise NotImplementedError
