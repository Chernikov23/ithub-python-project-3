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
	pass

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
	pass