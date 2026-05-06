from datetime import UTC, datetime
from typing import Literal, Annotated, Optional

from pydantic import BaseModel as PBaseModel
from pydantic import ConfigDict, computed_field, field_serializer, field_validator, StringConstraints, AfterValidator, Field


UsernameType = Annotated[str, StringConstraints(strip_whitespace=True, min_length=3, max_length=32, to_lower=True, pattern=r"^[a-zA-Z0-9._-]+$")]
PasswordType = Annotated[str, StringConstraints(min_length=8, max_length=32, pattern=r"^[a-zA-Z0-9!@#$%&?.]+$")]
BioType = Annotated[Optional[str], StringConstraints(min_length=0, max_length=2048, strip_whitespace=True, pattern=r"^[a-zA-Zа-яА-Я0-9'\".,!@#$%&*()-_=+/~— ]+$")]
DreamDescriptionType = Annotated[str, StringConstraints(min_length=5, max_length=16384, strip_whitespace=True, pattern=r"^[a-zA-Zа-яА-Я0-9'\".,!@#$%&*()-_=+/~— ]+$")]
DatetimeType = Annotated[str, StringConstraints(pattern=r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}Z$")]
IndexType = Annotated[int, Field(ge=0)]
CountType = IndexType
JwtType = Annotated[str, StringConstraints(pattern=r"^[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*$")]
RoleType = Literal['user', 'superuser']

class BaseModel(PBaseModel):
	"""
	Расширенная базовая модель, позволяет 
	красивее обрабатывать данные ORM-слоя 
	(правда отдельным методом, который вам 
	придётся разузнать)
	"""
	
	model_config = ConfigDict(
		populate_by_name=True, from_attributes=True
	)


class UserToken(BaseModel):
	"""
	Схема Oauth2-токена
	"""
	
	access_token: JwtType
	token_type: Literal['bearer'] = 'bearer'


class Username(BaseModel):
	"""
	Имя пользователя

	:username: имя пользователя (строка)
	"""

	username: UsernameType


class UserCreate(BaseModel):
	"""
	Создание пользователя

	:username: имя пользователя (строка ненулевой длины)
	:password: хешированный пароль
	:bio: биография (опциональное строковое поле) 
	"""

	username: UsernameType
	password: PasswordType
	bio: BioType | None = None


class UserUpdate(BaseModel):
	"""
	Обновление биографии пользователя

	:bio: биография (опциональное строковое поле)
	"""

	bio: BioType | None


class UserProfile(BaseModel):
	"""
	Публичная схема пользователя

	:username: имя пользователя
	:bio: биография (опциональное строковое поле)
	"""

	username: UsernameType
	bio: BioType | None


class UserAccount(BaseModel):
	"""
	Приватная схема пользователя
	
	:username: имя пользователя
	:bio: биография (опциональное строковое поле)
	:role: роль пользователя
	"""

	username: UsernameType
	bio: BioType | None
	role: RoleType


class NewDream(BaseModel):
	"""
	Создание нового сна

	:description: описание сна (строка минимальной длины 5)
	"""

	description: DreamDescriptionType


class Dream(BaseModel):
	"""
	Основная схема для операций по снам
	:id: целочисленный идентификатор
	:description: тело сна (строка)
	:author: объект схемы UserProfile
	:created_at: utc-datetime в ISO-формате
	:favorited_by: список лайкнувших пользователей (список строк)
	"""

	id: IndexType
	description: DreamDescriptionType
	author: UserProfile
	created_at: DatetimeType
	favorited_by: list[UsernameType]

	@field_validator('author', mode='before')
	@classmethod
	def convert_to_profile(cls, value):
		if isinstance(value, UserProfile):
			return value
		return UserProfile.model_validate(value)
	

	@field_serializer('created_at')
	def convert_created_at(self, created_at: datetime) -> str:
		return datetime.fromisoformat(created_at).isoformat() + 'Z'


	@computed_field
	def favorites_count(self) -> int:
		return len(self.favorited_by)


class MultipleDreams(BaseModel):
	"""
	Схема для списка снов

	:dreams: список объектов схемы Dream
	:dreams_count: количество снов подвыборки (целое число)
	"""

	dreams: list[Dream]
	dreams_count: CountType