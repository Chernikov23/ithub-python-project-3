
from fastapi import APIRouter, Body, Path, status

from app import schema
from app.api.dependencies import CurrentUser, SessionDatabase
from app.api.exceptions import *
from app.services import users_service as usersvc

users_router = APIRouter(
	prefix='/users',
	tags=['Пользователи'],
)


@users_router.get(
	'/me',
	summary='Информация о текущем залогиненном пользователе',
	response_model=schema.UserAccount,
	responses={
		status.HTTP_401_UNAUTHORIZED: {'description': 'Ошибка токена или пользовательских данных'},
	},
)
def get_current(
	current_user: CurrentUser,
) -> schema.UserAccount:
	"""
	Получает текущего пользователя через инъекцию зависимостей, в случае
	ошибки выбрасывает CredentialsHTTPException. Иначе - отвечает согласно схеме.
	"""

	return current_user


@users_router.get(
	'/{username}',
	summary='Информация о пользователе по юзернейму',
	description='Публичная часть информации о пользователе по юзернейму',
	response_model=schema.UserProfile,
	responses={
		status.HTTP_404_NOT_FOUND: {'description': 'Пользователь не найден'},
		status.HTTP_422_UNPROCESSABLE_CONTENT: {'description': 'Юзернейм не валиден'},
	},
)
def get_by_username(
	session: SessionDatabase,
	username: schema.UsernameType = Path(..., description='Имя пользователя'),
) -> schema.UserProfile:
	"""
	Запрашивает users_service на получение пользователя по юзернейму.
	Если пользователь не найден, выбрасывает NotFoundHTTPException c
	пояснением. Иначе - отвечает согласно схеме.
	"""

	user = usersvc.get_by_username(session=session, username=username)

	if not user:
		raise NotFoundHTTPException('Имя пользователя не найдено.')

	return schema.UserProfile(username=user.username, bio=user.bio)


@users_router.delete(
	'/{username}',
	summary='Удалить пользователя по юзернейму',
	description='Суперпользователь может удалить пользователя по юзернейму',
	responses={status.HTTP_422_UNPROCESSABLE_CONTENT: {'description': 'Юзернейм не валиден'},
			status.HTTP_403_FORBIDDEN: {'description': 'Отказано в доступе'}},
)
def delete_by_username(
	session: SessionDatabase,
	current_user: CurrentUser,
	username: schema.UsernameType = Path(..., description='Имя пользователя'),
) -> None:
	"""
	Запрашивает users_service на удаление пользователя по юзернейму.
	Если пользователь не найден, выбрасывает NotFoundHTTPException c
	пояснением. Иначе - отвечает согласно схеме.
	"""

	if current_user.role != 'superuser':
		return AccessDeniedHTTPException()

	usersvc.delete(session=session, username=username)


@users_router.put(
	'/',
	summary='Обновление данных залогиненного пользователя',
	response_model=schema.UserProfile,
	status_code=200,
	responses={
		status.HTTP_401_UNAUTHORIZED: {'description': 'Ошибка токена или пользовательских данных'},
		status.HTTP_404_NOT_FOUND: {'description': 'Пользователь не найден'},
		status.HTTP_422_UNPROCESSABLE_CONTENT: {'description': 'Данные не валидны'},
	},
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

	user = usersvc.update(
		session=session, username=current_user.username, update_data=update_user_payload
	)

	if not user:
		raise NotFoundHTTPException()

	return user

@users_router.put(
	'/{username}',
	summary='Изменить данные пользователя по юзернейму',
	description='Суперпользователь может изменить данные пользователя по юзернейму',
	response_model=schema.UserProfile,
	status_code=200,
	responses={
		status.HTTP_401_UNAUTHORIZED: {'description': 'Ошибка токена или пользовательских данных'},
		status.HTTP_404_NOT_FOUND: {'description': 'Пользователь не найден'},
		status.HTTP_422_UNPROCESSABLE_CONTENT: {'description': 'Данные не валидны'},
	},
)
def update_by_username(
	session: SessionDatabase,
	current_user: CurrentUser,
	username: schema.UsernameType = Path(..., description='Имя пользователя'),
	update_user_payload: schema.UserUpdate = Body(...),
	status_code=200,
	responses={
		status.HTTP_401_UNAUTHORIZED: {'description': 'Ошибка токена или пользовательских данных'},
		status.HTTP_404_NOT_FOUND: {'description': 'Пользователь не найден'},
		status.HTTP_422_UNPROCESSABLE_CONTENT: {'description': 'Данные не валидны'},
	},
	response_model=schema.UserProfile
) -> schema.UserProfile:
	"""
	Запрашивает users_service на изменение данных пользователя по юзернейму.
	Если пользователь не найден, выбрасывает NotFoundHTTPException c
	пояснением. Иначе - отвечает согласно схеме.
	"""

	if current_user.role != 'superuser':
		raise AccessDeniedHTTPException()
	
	user = usersvc.update(session=session, username=username, update_data=update_user_payload)

	if not user:
		raise NotFoundHTTPException()

	return user