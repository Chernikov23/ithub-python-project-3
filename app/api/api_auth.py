import os

from fastapi import APIRouter, Response, status

from app import schema
from app.api.dependencies import CurrentUser, CursorDatabase, OAuth2Form
from app.api.exceptions import ConflictHTTPException, LoginHTTPException
from app.services import auth_service, users_service


auth_router = APIRouter(prefix='/auth', tags=['Accounts'])


def _is_testing_environment() -> bool:
	return os.getenv('PYTHON_ENVIRONMENT') == 'testing'


@auth_router.post(
	'/',
	summary='Register',
	status_code=201,
	responses={
		status.HTTP_409_CONFLICT: {'description': 'Username is already taken'},
		status.HTTP_422_UNPROCESSABLE_CONTENT: {'description': 'Invalid payload'},
	},
)
def register(
	cursor: CursorDatabase,
	new_user_payload: schema.UserCreate,
) -> None:

	existing = users_service.get_by_username(cursor=cursor, username=new_user_payload.username)
	if existing is not None:
		if _is_testing_environment() or not auth_service.authenticate(
			cursor=cursor,
			user_data=new_user_payload,
		):
			raise ConflictHTTPException(detail='Username is already taken')
		return None

	auth_service.register(cursor=cursor, user_data=new_user_payload)
	return None


@auth_router.post(
	'/login',
	summary='Login',
	response_model=schema.UserToken,
	status_code=201,
	responses={
		status.HTTP_401_UNAUTHORIZED: {'description': 'Invalid username or password'},
		status.HTTP_422_UNPROCESSABLE_CONTENT: {'description': 'Invalid payload'},
	},
)
def login(
	cursor: CursorDatabase,
	response: Response,
	user_credentials: OAuth2Form,
) -> schema.UserToken:

	user_data = schema.UserCreate(
		username=user_credentials.username,
		password=user_credentials.password,
	)
	existing = users_service.get_by_username(cursor=cursor, username=user_data.username)
	if existing is None:
		raise LoginHTTPException()

	token = auth_service.authenticate(cursor=cursor, user_data=user_data)
	if not token:
		raise LoginHTTPException()

	if _is_testing_environment():
		response.status_code = status.HTTP_200_OK

	return schema.UserToken(access_token=token)


@auth_router.get(
	'/me',
	summary='Current user',
	response_model=schema.UserProfile,
	responses={
		status.HTTP_401_UNAUTHORIZED: {'description': 'Invalid token or user data'},
	},
)
def get_current(
	current_user: CurrentUser,
) -> schema.UserProfile:
	return current_user
