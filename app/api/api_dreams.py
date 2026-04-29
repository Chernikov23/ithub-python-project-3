from fastapi import APIRouter, Path, Query, status

from app import schema
from app.api.exceptions import (
	ConflictHTTPException,
	NotFoundHTTPException,
	CredentialsHTTPException,
)
from app.api.dependencies import CurrentUser, SessionDatabase
from app.database.exceptions import DuplicateDatabaseException
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
) -> schema.MultipleDreams:
	"""
	Запрашивает dreams_service, возвращает результат согласно схеме.

	Примечание: здесь и далее при сериализации ответа будет красиво
	воспользоваться упомянутым в schema.py методом валидации ORM-слоя
	"""

	raise NotImplementedError


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
	"""
	Получает текущего пользователя через инъекцию зависимостей,
	в случае ошибки выбрасывает CredentialsHTTPException.
	Иначе - запрашивает dreams_service на создание сна. В случае
	ошибки дублирования выбрасывает ConflictHTTPException с пояснением.
	Иначе - возвращает результат согласно схеме.
	"""

	raise NotImplementedError


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
	Запрашивает dreams_service на получение сна по идентификатору.
	Если сон не найден, выбрасывает NotFoundHTTPException c пояснением.
	Иначе - возвращает результат согласно схеме
	"""

	raise NotImplementedError


@dreams_router.delete(
	'/{id}',
	summary='Удаление сна',
	description='Удаление сна (требуется авторизация для удаления собственных снов',
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
	"""
	Получает текущего пользователя через инъекцию зависимостей,
	в случае ошибки выбрасывает CredentialsHTTPException.
	Иначе - запрашивает dreams_service на получение сна по идентификатору.
	Если сон не найден, выбрасывает NotFoundHTTPException c пояснением.
	Иначе - проверяет, является ли текущий пользователь автором сна, который
	он хочет удалить. Если нет - выбрасывает исключение c пояснением.
	Иначе - запрашивает dreams_service на удаление сна.
	"""

	raise NotImplementedError
