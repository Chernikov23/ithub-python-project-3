from sqlalchemy.orm import Session
from app import schema
from app.database import models
from app.security import create_access_token, get_password_hash, verify_password
from app.services import users_service

def register(*, session: Session, user_data: schema.UserCreate) -> None:
	hashed = get_password_hash(user_data.password)
	
	new_user = models.User(
		username=user_data.username,
		password=hashed
	)
	session.add(new_user)
	session.commit()      # ИСПРАВЛЕНО: Меняем flush на commit для регистрации
	session.expire_all()  # Очищаем кэш


def authenticate(*, session: Session, user_data: schema.UserCreate) -> str | None:
	session.expire_all()
	user = users_service.get_user_with_password(session=session, username=user_data.username)
	
	if not user:
		return None
	
	username, hashed = user

	if not verify_password(user_data.password, hashed):
		return None
	
	return create_access_token(subject=username)
