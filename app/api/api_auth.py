from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse

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
	"""
	Запрашивает users_service на предмет наличия пользователя с переданным именем.
	Если пользователь найден, выбрасывает ConflictHTTPException с пояснением.
	Иначе - проводит регистрацию через auth_service.
	"""

	if users_service.get_by_username(session=session, username=new_user_payload.username):
		raise ConflictHTTPException(detail='Выбранный юзернейм занят')

	auth_service.register(session=session, user_data=new_user_payload)


@auth_router.post(
	'/login',
	summary='Логин',
	response_model=schema.UserToken,
	status_code=status.HTTP_200_OK,
	responses={
		status.HTTP_401_UNAUTHORIZED: {'description': 'Некорректное имя или пароль'},
		status.HTTP_422_UNPROCESSABLE_CONTENT: {'description': 'Данные не валидны'},
	},
)
def login(
	request: Request,
	session: SessionDatabase,
	user_credentials: OAuth2Form,
) -> JSONResponse:
	"""
	Запрашивает users_service на предмет наличия пользователя с переданным именем.
	Если пользователь не найден, выбрасывает LoginHTTPException с пояснением.
	Иначе - запрашивает аутентификацию через auth_service. Если пароль некорректен,
	выбрасывает LoginHTTPException с пояснением. Иначе - возвращает токен согласно схеме.
	"""

	user = users_service.get_by_username(session=session, username=user_credentials.username)
	if not user:
		raise LoginHTTPException()

	token = auth_service.authenticate(
		session=session,
		user_data=schema.UserCreate(
			username=user_credentials.username,
			password=user_credentials.password,
		),
	)
	if token is None:
		raise LoginHTTPException()

	response_data = schema.UserToken(access_token=token).model_dump()
	status_code = status.HTTP_201_CREATED if request.headers.get('X-Requested-With') == 'XMLHttpRequest' else status.HTTP_200_OK
	return JSONResponse(content=response_data, status_code=status_code)


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

	return current_user
