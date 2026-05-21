from fastapi import APIRouter, status, Depends
from app import schema
from app.api.dependencies import CurrentUser, CursorDatabase, OAuth2Form
from app.api.exceptions import (
    ConflictHTTPException,
    CredentialsHTTPException,
    LoginHTTPException,
)
from app.services import auth_service, users_service

# Создаем роутер с именем auth_router
auth_router = APIRouter(prefix='/auth', tags=['Аккаунты'])

@auth_router.post('/', status_code=201)
def register(cursor: CursorDatabase, new_user_payload: schema.UserCreate):
    existing = users_service.get_by_username(cursor=cursor, username=new_user_payload.username)
    if existing:
        raise ConflictHTTPException(detail='Выбранный юзернейм занят')
    auth_service.register(cursor=cursor, user_data=new_user_payload)
    return {"message": "User created"}

@auth_router.post('/login', response_model=schema.UserToken)
def login(cursor: CursorDatabase, user_credentials: OAuth2Form):
    user_data = schema.UserCreate(username=user_credentials.username, password=user_credentials.password)
    token = auth_service.authenticate(cursor=cursor, user_data=user_data)
    if token is None:
        raise LoginHTTPException()
    return schema.UserToken(access_token=token)

@auth_router.get('/me', response_model=schema.UserProfile)
def get_current(current_user: CurrentUser):
    return current_user
