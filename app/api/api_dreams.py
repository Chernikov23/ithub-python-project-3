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
	favorited: str = Query(None, title='Фильтр по любимым снам юзернейма'),
) -> schema.MultipleDreams:
	result, count = dreams_service.get_list(
		session=session,
		limit=limit,
		offset=offset,
		author=author,
		favorited=favorited,
		search=search,
	)
	return schema.MultipleDreams(
		dreams=[schema.Dream.model_validate(dream) for dream in result],
		dreams_count=count,
	)


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
	try:
		dream = dreams_service.create(session=session, new_dream=new_dream, author=current_user)
		return schema.Dream.model_validate(dream)
	except DuplicateDreamException:
		raise ConflictHTTPException("Пользователь уже добавлял этот сон")


@dreams_router.get(
	'/{id}',
	summary='Чтение сна',
	response_model=schema.Dream,
)
def get(
	session: SessionDatabase,
	id: int = Path(..., title='Идентификатор сна для чтения'),
) -> schema.Dream:
	dream = dreams_service.get_by_id(session=session, id=id)
	if not dream:
		raise HTTPException(status_code=404, detail='No dream found')
	return schema.Dream.model_validate(dream)


@dreams_router.delete(
	'/{id}',
	summary='Удаление сна',
	description='Удаление сна (требуется авторизация для удаления собственных снов и админправа для удаления чужих снов',
	status_code=204,
)
def delete(
	current_user: CurrentUser,
	session: SessionDatabase,
	id: int = Path(..., title='Идентификатор сна для удаления'),
) -> None:
	dream = dreams_service.get_by_id(session=session, id=id)

	if not dream:
		raise HTTPException(status_code=404, detail='Сон не найден')

	if dream.author != current_user:
		raise HTTPException(status_code=403, detail='Вы не являетесь автором этого сна')

	dreams_service.delete(session=session, dream_id=id)


@dreams_router.post(
	'/{id}/favorite',
	summary='Добавить сон в любимые',
	description='Добавить сон в любимые (требуется авторизация)',
	response_model=schema.Dream,
)
def favorite(
	current_user: CurrentUser,
	session: SessionDatabase,
	id: int = Path(..., title='Идентификатор сна для лайка'),
) -> schema.Dream:
	dream = dreams_service.get_by_id(session=session, id=id)
	if not dream:
		raise HTTPException(status_code=404, detail='No dream found')

	dreams_service.favorite(session=session, dream=dream, user=current_user)
	return schema.Dream.model_validate(dream)


@dreams_router.delete(
	'/{id}/favorite',
	summary='Снять лайк',
	description='Снять лайк со сна (требуется авторизация)',
	response_model=schema.Dream,
)
def unfavorite(
	current_user: CurrentUser,
	session: SessionDatabase,
	id: int = Path(..., title='Идентификатор сна для снятия лайка'),
) -> schema.Dream:
	dream = dreams_service.get_by_id(session=session, id=id)
	if not dream:
		raise HTTPException(status_code=404, detail='Сон не найден')

	dreams_service.favorite(session=session, dream=dream, user=current_user, favorite=False)
	return schema.Dream.model_validate(dream)
