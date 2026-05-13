from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel as PBaseModel
from pydantic import ConfigDict, Field, field_validator


class BaseModel(PBaseModel):
	"""
	Расширенная базовая модель, позволяет
	красивее обрабатывать данные ORM-слоя
	через метод model_validate.
	"""

	model_config = ConfigDict(populate_by_name=True, from_attributes=True)


class UserToken(BaseModel):
	"""
	Схема данных для oauth2-токенов, не требует изменений
	"""

	access_token: str
	token_type: Literal['bearer'] = 'bearer'


class UserCreate(BaseModel):
	"""
	Схема данных для создания пользователя

	:username: строка длиной не менее 2 символов
	:password: строка длиной не менее 8 символов
	"""

	username: str = Field(min_length=2)
	password: str = Field(min_length=8)


class UserProfile(BaseModel):
	"""
	Схема данных для публичной информации пользователя

	:username: строка
	"""

	username: str


class Dream(BaseModel):
	"""
	Схема для выдачи данных сна

	:id: целое число
	:description: строка описания
	:author: строка, юзернейм автора
	:created_at: строка, дататайм формата ISO
	"""

	id: int
	description: str
	author: str
	created_at: datetime

	@field_validator('author', mode='before')
	@classmethod
	def _author_username(cls, v: Any) -> str:
		if hasattr(v, 'username'):
			return str(v.username)
		return str(v)


class NewDream(BaseModel):
	"""
	Схема данных для создания нового сна

	:description: строка длиной не менее 5
	"""

	description: str = Field(min_length=5)


class MultipleDreams(BaseModel):
	"""
	:dreams: список Dream-ов
	:dreams_count: количество снов в подвыборке, целое число
	"""

	dreams: list[Dream]
	dreams_count: int