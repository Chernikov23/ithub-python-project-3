from fastapi import APIRouter, Body, HTTPException, Path

from app import schema
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
)
def get_current(
	current_user: CurrentUser,
) -> schema.UserProfile:
	return schema.UserProfile(bio=current_user.bio, username=current_user.username)


@users_router.get(
	'/{username}',
	summary='Информация о пользователе по юзернейму',
	description='Публичная часть информации о пользователе по юзернейму',
	response_model=schema.UserProfile,
)
def get_by_username(
	session: SessionDatabase,
	username: str = Path(..., description='Username of the profile to get'),
) -> schema.UserProfile:
	user = users_service.get_by_username(session=session, username=username)

	if not user:
		raise HTTPException(status_code=404, detail=f'Пользователь <{username}> не найден')

	return schema.UserProfile(bio=user.bio, username=user.username)


@users_router.put(
	'/',
	summary='Обновление данных залогиненного пользователя',
	response_model=schema.UserProfile,
)
def update_current(
	current_user: CurrentUser,
	session: SessionDatabase,
	update_user: schema.UserUpdate = Body(...),
) -> schema.UserProfile:
	user = users_service.get_by_username(session=session, username=current_user.username)

	if not user:
		raise HTTPException(status_code=401, detail='Отсутствуют пользовательские данные')

	user = users_service.update(session=session, db_obj=current_user, obj_in=update_user)

	return schema.UserProfile(username=user.username, bio=user.bio)
