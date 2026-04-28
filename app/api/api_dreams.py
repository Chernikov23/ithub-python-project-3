from fastapi import APIRouter, HTTPException, Path, Query

from app import schema
from app.api.exceptions import ConflictHTTPException
from app.api.dependencies import CurrentUser, SessionDatabase
from app.database.exceptions import DuplicateDreamException
from app.services import dreams_service

dreams_router = APIRouter(
	prefix='/dreams',
	tags=['Сны'],
)


@dreams_router.get(
	'/',
	summary='Чтение снов',
	description='Чтение снов с возможностью поиска, фильтрации, пагинации, с сортировкой по времени добавления',
	response_model=schema.MultipleDreams,
)
def get_list(
	session: SessionDatabase,
	limit: int = Query(20, title='Количество снов (по умолчанию 20)'),
	offset: int = Query(0, title='Величина отступа (по умолчанию  0)'),
	author: str = Query(None, title='Фильтр по юзернейму автора'),
	search: str = Query(None, title='Поиск по тексту'),
) -> schema.MultipleDreams:
	pass


@dreams_router.post(
	'/',
	summary='Добавление сна',
	description='Добавление сна (требуется авторизация)',
	response_model=schema.Dream,
	status_code=201,
)
def create(
	current_user: CurrentUser,
	session: SessionDatabase,
	new_dream: schema.NewDream,
) -> schema.Dream:
	pass


@dreams_router.get(
	'/{id}',
	summary='Чтение сна',
	response_model=schema.Dream,
)
def get(
	session: SessionDatabase,
	id: int = Path(..., title='Идентификатор сна для чтения'),
) -> schema.Dream:
	pass


@dreams_router.delete(
	'/{id}',
	summary='Удаление сна',
	description='Удаление сна (требуется авторизация для удаления собственных снов',
	status_code=204,
)
def delete(
	current_user: CurrentUser,
	session: SessionDatabase,
	id: int = Path(..., title='Идентификатор сна для удаления'),
) -> None:
	pass
