from fastapi import APIRouter, Path, Query, status

from app import schema
from app.api.dependencies import CurrentUser, SessionDatabase
from app.api.exceptions import (
	ConflictHTTPException,
	NotAuthorizedHTTPException,
	NotFoundHTTPException,
)
from app.database.exceptions import DuplicateDatabaseException
from app.services import dreams_service

dreams_router = APIRouter(
	prefix='/dreams',
	tags=['Сны'],
)


@dreams_router.get(
	'/',
	summary='Чтение снов',
	description=(
		'Чтение снов с возможностью поиска, фильтрации, '
		'пагинации, с сортировкой по времени добавления'
	),
	response_model=schema.MultipleDreams,
	responses={
		status.HTTP_422_UNPROCESSABLE_CONTENT: {'description': 'Параметры запроса не валидные'}
	},
)
def get_dreams_list(
	session: SessionDatabase,
	limit: int = Query(20, ge=1, title='Количество снов (по умолчанию 20)'),
	offset: int = Query(0, ge=0, title='Величина отступа (по умолчанию  0)'),
	author: str | None = Query(None, title='Фильтр по юзернейму автора'),
) -> schema.MultipleDreams:
	"""
	Запрашивает dreams_service, возвращает результат согласно схеме.
	"""

	dreams, dreams_count = dreams_service.get_list(
		session=session,
		limit=limit,
		offset=offset,
		author=author,
	)
	return schema.MultipleDreams(
		dreams=[schema.Dream.model_validate(d) for d in dreams],
		dreams_count=dreams_count,
	)


@dreams_router.post(
	'/',
	summary='Добавление сна',
	description='Добавление сна (требуется авторизация)',
	response_model=schema.Dream,
	status_code=status.HTTP_201_CREATED,
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
	"""
	Создает новый сон от имени текущего пользователя.
	"""

	try:
		dream = dreams_service.create(
			session=session,
			new_dream=new_dream_payload,
			author=current_user,
		)
	except DuplicateDatabaseException as exc:
		raise ConflictHTTPException(detail='Такой сон уже добавлен') from exc

	return schema.Dream.model_validate(dream)


@dreams_router.get(
	'/{id}',
	summary='Чтение сна',
	response_model=schema.Dream,
	responses={
		status.HTTP_404_NOT_FOUND: {'description': 'Сон не найден'},
		status.HTTP_422_UNPROCESSABLE_CONTENT: {'description': 'Идентификатор не валиден'},
	},
)
def get_dream(
	session: SessionDatabase,
	id: int = Path(..., title='Идентификатор сна для чтения'),
) -> schema.Dream:
	"""
	Получает сон по идентификатору. Если не найден - 404.
	"""

	dream = dreams_service.get_by_id(session=session, id=id)
	if dream is None:
		raise NotFoundHTTPException(detail='Сон не найден')
	return schema.Dream.model_validate(dream)


@dreams_router.delete(
	'/{id}',
	summary='Удаление сна',
	description='Удаление сна (требуется авторизация для удаления собственных снов)',
	status_code=status.HTTP_204_NO_CONTENT,
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
	"""
	Удаляет собственный сон по идентификатору.
	"""

	dream = dreams_service.get_by_id(session=session, id=id)
	if dream is None:
		raise NotFoundHTTPException(detail='Сон не найден')

	if dream.author_id != current_user.username:
		raise NotAuthorizedHTTPException(detail='Вы не являетесь автором сна')

	dreams_service.delete(session=session, dream_id=id)
