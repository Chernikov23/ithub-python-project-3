from fastapi import APIRouter, Path, Query, status

from app import schema
from app.api.dependencies import CurrentUser, SessionDatabase
from app.api.exceptions import *
from app.database.exceptions import *
from app.services import dreams_service as dreamsvc


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
		status.HTTP_422_UNPROCESSABLE_CONTENT: { "description": "Параметры запроса не валидные"}	
	}
)
def get_dreams_list(
	session: SessionDatabase,
	limit: int = Query(20, title='Количество снов (по умолчанию 20)'),
	offset: int = Query(0, title='Величина отступа (по умолчанию  0)'),
	author: str = Query(None, title='Фильтр по юзернейму автора'),
	search: str = Query(None, title='Поиск по тексту'),
	favorited: str = Query(None, title='Фильтр по любимым снам юзернейма'),
) -> schema.MultipleDreams:
	"""
	Запрашивает dreams_service, возвращает результат согласно схеме.
	
	Примечание: здесь и далее при сериализации ответа будет красиво 
	воспользоваться упомянутым в schema.py методом валидации ORM-слоя
	"""

	return dreamsvc.get_list(session=session, limit=limit, offset=offset,
							author=author, search=search, favorited=favorited)


@dreams_router.post(
	'/',
	summary='Добавление сна',
	description='Добавление сна (требуется авторизация)',
	response_model=schema.Dream,
	status_code=201,
	responses={
		status.HTTP_401_UNAUTHORIZED: { "description": "Ошибка токена или пользовательских данных" },
		status.HTTP_409_CONFLICT: { "description": "Пользователь уже добавлял этот сон" },
		status.HTTP_422_UNPROCESSABLE_CONTENT: { "description": "Данные не валидны" }
	}
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

	try:
		return dreamsvc.create(session=session, new_dream=new_dream_payload, author=current_user)
	except DuplicateDatabaseException:
		raise ConflictHTTPException('Сон с таким описанием уже существует.')

@dreams_router.get(
	'/{id}',
	summary='Чтение сна',
	response_model=schema.Dream,
	responses={
		status.HTTP_401_UNAUTHORIZED: { "description": "Ошибка токена или пользовательских данных" },
		status.HTTP_404_NOT_FOUND: { "description": "Сон не найден" },
		status.HTTP_422_UNPROCESSABLE_CONTENT: { "description": "Идентификатор не валиден" }
	}
)
def get_dream(
	session: SessionDatabase,
	id: schema.IndexType = Path(..., title='Идентификатор сна для чтения'),
) -> schema.Dream:
	"""
	Запрашивает dreams_service на получение сна по идентификатору.
	Если сон не найден, выбрасывает NotFoundHTTPException c пояснением.
	Иначе - возвращает результат согласно схеме
	"""
	dream = dreamsvc.get_by_id(session=session, id=id)

	if not dream:
		raise NotFoundHTTPException('Сон не найден.')
	
	return dream


@dreams_router.delete(
	'/{id}',
	summary='Удаление сна',
	description='Удаление сна (требуется авторизация для удаления собственных снов и админправа для удаления чужих снов',
	status_code=204,
	responses={
		status.HTTP_401_UNAUTHORIZED: { "description": "Ошибка токена или пользовательских данных" },
		status.HTTP_404_NOT_FOUND: { "description": "Сон не найден" },
		status.HTTP_403_FORBIDDEN: { "description": "Пользователь не является автором сна" },
		status.HTTP_422_UNPROCESSABLE_CONTENT: { "description": "Идентификатор не валиден" }
	}
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

	dream = dreamsvc.get_by_id(session=session, id=id)

	if not dream:
		raise NotFoundHTTPException('Сон не найден.')
	
	if dream.author.username != current_user.username and current_user.role != 'superuser':
		raise AccessDeniedHTTPException()

	dreamsvc.delete(session=session, dream_id=id)

@dreams_router.post(
	'/{id}/favorite',
	summary='Добавить сон в любимые',
	description='Добавить сон в любимые (требуется авторизация)',
	response_model=schema.Dream,
	responses={
		status.HTTP_401_UNAUTHORIZED: { "description": "Ошибка токена или пользовательских данных" },
		status.HTTP_404_NOT_FOUND: { "description": "Сон не найден" },
		status.HTTP_409_CONFLICT: { "description": "Сон уже добавлен пользователем в любимые" },
		status.HTTP_422_UNPROCESSABLE_CONTENT: { "description": "Идентификатор не валиден" }
	}
)
def favorite(
	current_user: CurrentUser,
	session: SessionDatabase,
	id: int = Path(..., title='Идентификатор сна для добавления в любимые'),
) -> schema.Dream:
	"""
	Получает текущего пользователя через инъекцию зависимостей,
	в случае ошибки выбрасывает CredentialsHTTPException.
	Иначе - запрашивает dreams_service на получение сна по идентификатору.
	Если сон не найден, выбрасывает NotFoundHTTPException c пояснением.
	Иначе - запрашивает dreams_service на добавление в любимые. Если сон 
	уже был добавлен пользователем в любимые, выбрасывает ConflictHTTPException
	c пояснением. Иначе - возвращает измененные данные согласно схеме.
	"""

	dream = dreamsvc.get_by_id(session=session, id=id)

	if not dream:
		raise NotFoundHTTPException('Сон не найден.')
	
	dreamsvc.favorite(session=session, dream=dream, user=current_user)

	return dreamsvc.get_by_id(session=session, id=id)


@dreams_router.delete(
	'/{id}/favorite',
	summary='Снять лайк',
	description='Снять лайк со сна (требуется авторизация)',
	response_model=schema.Dream,
	responses={
		status.HTTP_401_UNAUTHORIZED: { "description": "Ошибка токена или пользовательских данных" },
		status.HTTP_404_NOT_FOUND: { "description": "Сон не найден" },
		status.HTTP_409_CONFLICT: { "description": "Сон уже добавлен пользователем в любимые" },
		status.HTTP_422_UNPROCESSABLE_CONTENT: { "description": "Идентификатор не валиден" }
	}
)
def unfavorite(
	current_user: CurrentUser,
	session: SessionDatabase,
	id: int = Path(..., title='Идентификатор сна для удаления из любимых'),
) -> schema.Dream:
	"""
	Получает текущего пользователя через инъекцию зависимостей,
	в случае ошибки выбрасывает CredentialsHTTPException.
	Иначе - запрашивает dreams_service на получение сна по идентификатору.
	Если сон не найден, выбрасывает NotFoundHTTPException c пояснением.
	Иначе - запрашивает dreams_service на удаление из любимых любимые. Если сон 
	не был добавлен пользователем в любимые, выбрасывает ConflictHTTPException
	c пояснением. Иначе - возвращает измененные данные согласно схеме.
	"""

	dream = dreamsvc.get_by_id(session=session, id=id)

	if not dream:
		raise NotFoundHTTPException('Сон не найден.')
	
	dreamsvc.unfavorite(session=session, dream=dream, user=current_user)

	return dreamsvc.get_by_id(session=session, id=id)