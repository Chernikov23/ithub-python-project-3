from fastapi import APIRouter, Body, Path, status

from app import schema
from app.api.exceptions import CredentialsHTTPException, NotFoundHTTPException
from app.api.dependencies import CurrentUser, SessionDatabase
from app.services import users_service


users_router = APIRouter(
	prefix='/users',
	tags=['Пользователи'],
)


@users_router.get(
	'/me',
	summary='Информация о текущем залогиненном пользователе',
	response_model=schema.UserProfile,
	responses={
		status.HTTP_401_UNAUTHORIZED: { "description": "Ошибка токена или пользовательских данных" },
	}
)
def get_current(
	current_user: CurrentUser,
) -> schema.UserProfile:
	"""
	Получает текущего пользователя через инъекцию зависимостей, в случае 
	ошибки выбрасывает CredentialsHTTPException. Иначе - отвечает согласно схеме.
	"""

	raise NotImplementedError


@users_router.get(
	'/{username}',
	summary='Информация о пользователе по юзернейму',
	description='Публичная часть информации о пользователе по юзернейму',
	response_model=schema.UserProfile,
	responses={
		status.HTTP_404_NOT_FOUND: { "description": "Пользователь не найден" },
		status.HTTP_422_UNPROCESSABLE_CONTENT: { "description": "Юзернейм не валиден" }
	}
)
def get_by_username(
	session: SessionDatabase,
	username: str = Path(..., description='Имя пользователя'),
) -> schema.UserProfile:
	"""
	Запрашивает users_service на получение пользователя по юзернейму.
	Если пользователь не найден, выбрасывает NotFoundHTTPException c
	пояснением. Иначе - отвечает согласно схеме.
	"""

	raise NotImplementedError


@users_router.put(
	'/',
	summary='Обновление данных залогиненного пользователя',
	response_model=schema.UserProfile,
	status_code=200,
	responses={
		status.HTTP_401_UNAUTHORIZED: { "description": "Ошибка токена или пользовательских данных" },
		status.HTTP_404_NOT_FOUND: { "description": "Пользователь не найден" },
		status.HTTP_422_UNPROCESSABLE_CONTENT: { "description": "Данные не валидны" }
	}
)
def update_current(
	current_user: CurrentUser,
	session: SessionDatabase,
	update_user_payload: schema.UserUpdate = Body(...),
) -> schema.UserProfile:
	"""
	Получает текущего пользователя через инъекцию зависимостей, в случае 
	ошибки выбрасывает CredentialsHTTPException. Иначе - запрашивает пользователя
	через users_service. Если пользователь не найден, выбрасывает NotFoundHTTPException 
	с пояснением. Иначе - запрашивает users_service на обновление данных. Возвращает
	ответ согласно схеме.
	"""
	
	raise NotImplementedError
