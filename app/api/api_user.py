from fastapi import APIRouter, Body, Path, status

from app import schema
from app.api.dependencies import CurrentUser, CursorDatabase
from app.api.exceptions import NotFoundHTTPException
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
		status.HTTP_401_UNAUTHORIZED: {'description': 'Ошибка токена или пользовательских данных'},
	},
)
def get_current(
	current_user: CurrentUser,
) -> schema.UserProfile:
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
	cursor: CursorDatabase,
	username: str = Path(..., description='Имя пользователя'),
) -> schema.UserProfile:
	user = users_service.get_by_username(cursor=cursor, username=username)

	if user is None:
		raise NotFoundHTTPException(detail='Пользователь не найден')

	return user


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
	cursor: CursorDatabase,
	update_user_payload: schema.UserUpdate = Body(default_factory=schema.UserUpdate),
) -> schema.UserProfile:
	updated_user = users_service.update(
		cursor=cursor,
		username=current_user.username,
		update_data=update_user_payload,
	)

	if updated_user is None:
		raise NotFoundHTTPException(detail='Пользователь не найден')

	return updated_user
