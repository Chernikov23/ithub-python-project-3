from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel as PBaseModel
from pydantic import ConfigDict, Field, field_serializer


class BaseModel(PBaseModel):
	"""
	Расширенная базовая модель, позволяет
	красивее обрабатывать данные ORM-слоя
	(правда отдельным методом, который вам
	придётся разузнать)
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
	TODO
	Схема данных для создания пользователя

	:username: строка длиной не менее 2 символов
	:password: строка длиной не менее 8 символов
	"""

	username: str = Field(..., min_length=2)
	password: str = Field(..., min_length=8)

	@field_serializer('username')
	def _strip_username(self, v: str) -> str:  # ensure no surrounding spaces
		return v.strip()


class UserProfile(BaseModel):
	"""
	TODO
	Схема данных для публичной информации пользователя

	:username: строка
	"""

	username: str


class Dream(BaseModel):
	"""
	TODO
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


class NewDream(BaseModel):
	description: str = Field(..., min_length=5)

	@field_serializer('description')
	def _strip_description(self, v: str) -> str:
		return v.strip()


class MultipleDreams(BaseModel):

	dreams: list[Dream]
	dreams_count: int
