from fastapi import APIRouter, Path, Query, status

from app import schema
from app.api.dependencies import CurrentUser, SessionDatabase
from app.api.exceptions import (
	ConflictHTTPException,
	NotAuthorizedHTTPException,
	NotFoundHTTPException,
)
from app.database.exceptions import DuplicateDatabaseException, NotFoundDatabaseException
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
	responses={
		status.HTTP_422_UNPROCESSABLE_CONTENT: {'description': 'Параметры запроса не валидные'}
	},
)
def get_dreams_list(
	session: SessionDatabase,
	limit: int = Query(20, title='Количество снов (по умолчанию 20)'),
	offset: int = Query(0, title='Величина отступа (по умолчанию  0)'),
	author: str = Query(None, title='Фильтр по юзернейму автора'),
	search: str = Query(None, title='Поиск по тексту'),
	favorited: str = Query(None, title='Фильтр по любимым снам юзернейма'),
) -> schema.MultipleDreams:
	dreams, dreams_count = dreams_service.get_list(
		session=session,
		limit=limit,
		offset=offset,
		author=author,
		search=search,
		favorited=favorited,
	)

	return schema.MultipleDreams.model_validate({'dreams': dreams, 'dreams_count': dreams_count})


@dreams_router.post(
	'/',
	summary='Добавление сна',
	description='Добавление сна (требуется авторизация)',
	response_model=schema.Dream,
	status_code=201,
	responses={
		status.HTTP_401_UNAUTHORIZED: {'description': 'Ошибка токена или пользовательских данных'},
		status.HTTP_409_CONFLICT: {'description': 'Пользователь уже добавлял этот сон'},
		status.HTTP_422_UNPROCESSABLE_CONTENT: {'description': 'Данные не валидны'},
	},
)
def create_dream(
	current_user: CurrentUser,
	session: SessionDatabase,
	new_dream_payload: schema.NewDream,
) -> schema.Dream:
	try:
		dream = dreams_service.create(
			session=session, new_dream=new_dream_payload, author=current_user
		)
	except DuplicateDatabaseException as error:
		raise ConflictHTTPException(detail='Пользователь уже добавлял этот сон') from error

	return schema.Dream.model_validate(dream)


@dreams_router.get(
	'/{id}',
	summary='Чтение сна',
	response_model=schema.Dream,
	responses={
		status.HTTP_401_UNAUTHORIZED: {'description': 'Ошибка токена или пользовательских данных'},
		status.HTTP_404_NOT_FOUND: {'description': 'Сон не найден'},
		status.HTTP_422_UNPROCESSABLE_CONTENT: {'description': 'Идентификатор не валиден'},
	},
)
def get_dream(
	session: SessionDatabase,
	id: int = Path(..., title='Идентификатор сна для чтения'),
) -> schema.Dream:
	dream = dreams_service.get_by_id(session, id)

	if dream is None:
		raise NotFoundHTTPException(detail='Сон не найден')

	return schema.Dream.model_validate(dream)


@dreams_router.delete(
	'/{id}',
	summary='Удаление сна',
	description='Удаление сна (требуется авторизация для удаления собственных снов и админправа для удаления чужих снов',
	status_code=204,
	responses={
		status.HTTP_401_UNAUTHORIZED: {'description': 'Ошибка токена или пользовательских данных'},
		status.HTTP_404_NOT_FOUND: {'description': 'Сон не найден'},
		status.HTTP_403_FORBIDDEN: {'description': 'Пользователь не является автором сна'},
		status.HTTP_422_UNPROCESSABLE_CONTENT: {'description': 'Идентификатор не валиден'},
	},
)
def delete(
	current_user: CurrentUser,
	session: SessionDatabase,
	id: int = Path(..., title='Идентификатор сна для удаления'),
) -> None:
	dream = dreams_service.get_by_id(session, id)

	if dream is None:
		raise NotFoundHTTPException(detail='Сон не найден')

	is_author = dream.author_id == current_user.username

	if not is_author and not current_user.is_superuser:
		raise NotAuthorizedHTTPException(detail='Пользователь не является автором сна')

	dreams_service.delete(session=session, dream_id=id)


@dreams_router.post(
	'/{id}/favorite',
	summary='Добавить сон в любимые',
	description='Добавить сон в любимые (требуется авторизация)',
	response_model=schema.Dream,
	responses={
		status.HTTP_401_UNAUTHORIZED: {'description': 'Ошибка токена или пользовательских данных'},
		status.HTTP_404_NOT_FOUND: {'description': 'Сон не найден'},
		status.HTTP_409_CONFLICT: {'description': 'Сон уже добавлен пользователем в любимые'},
		status.HTTP_422_UNPROCESSABLE_CONTENT: {'description': 'Идентификатор не валиден'},
	},
)
def favorite(
	current_user: CurrentUser,
	session: SessionDatabase,
	id: int = Path(..., title='Идентификатор сна для добавления в любимые'),
) -> schema.Dream:
	dream = dreams_service.get_by_id(session, id)

	if dream is None:
		raise NotFoundHTTPException(detail='Сон не найден')

	try:
		dreams_service.favorite(session=session, dream=dream, user=current_user)
	except DuplicateDatabaseException as error:
		raise ConflictHTTPException(detail='Сон уже добавлен пользователем в любимые') from error

	return schema.Dream.model_validate(dream)


@dreams_router.delete(
	'/{id}/favorite',
	summary='Снять лайк',
	description='Снять лайк со сна (требуется авторизация)',
	response_model=schema.Dream,
	responses={
		status.HTTP_401_UNAUTHORIZED: {'description': 'Ошибка токена или пользовательских данных'},
		status.HTTP_404_NOT_FOUND: {'description': 'Сон не найден'},
		status.HTTP_409_CONFLICT: {'description': 'Сон не был добавлен пользователем в любимые'},
		status.HTTP_422_UNPROCESSABLE_CONTENT: {'description': 'Идентификатор не валиден'},
	},
)
def unfavorite(
	current_user: CurrentUser,
	session: SessionDatabase,
	id: int = Path(..., title='Идентификатор сна для удаления из любимых'),
) -> schema.Dream:

	dream = dreams_service.get_by_id(session, id)

	if dream is None:
		raise NotFoundHTTPException(detail='Сон не найден')

	try:
		dreams_service.unfavorite(session=session, dream=dream, user=current_user)
	except NotFoundDatabaseException as error:
		raise ConflictHTTPException(detail='Сон не был добавлен пользователем в любимые') from error

	return schema.Dream.model_validate(dream)
