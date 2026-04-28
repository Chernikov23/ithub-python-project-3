from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel as PBaseModel
from pydantic import ConfigDict, Field, computed_field, field_serializer, field_validator


class BaseModel(PBaseModel):
	'''
	Расширенная базовая модель, позволяет 
	красивее обрабатывать данные ORM-слоя 
	(правда отдельным методом, который вам 
	придётся разузнать)
	'''
	
	model_config = ConfigDict(
		populate_by_name=True, from_attributes=True
	)


class UserToken(BaseModel):
	'''
	Схема Oauth2-токена
	'''
	
	access_token: str
	token_type: Literal['bearer'] = 'bearer'


class Username(BaseModel):
	"""
	Имя пользователя

	:username: имя пользователя (строка)
	"""

	pass


class UserCreate(BaseModel):
	"""
	Создание пользователя

	:username: имя пользователя (строка ненулевой длины)
	:password: хешированный пароль
	:bio: биография (опциональное строковое поле) 
	"""

	pass


class UserUpdate(BaseModel):
	"""
	Обновление биографии пользователя

	:bio: биография (опциональное строковое поле)
	"""

	pass


class UserProfile(BaseModel):
	"""
	Публичная схема пользователя

	:username: имя пользователя
	:bio: биография (опциональное строковое поле)
	"""

	pass


class NewDream(BaseModel):
	"""
	Создание нового сна

	:description: описание сна (строка минимальной длины 5)
	"""

	pass


class Dream(BaseModel):
	"""
	Основная схема для операций по снам
	:id: целочисленный идентификатор
	:description: тело сна (строка)
	:author: объект схемы UserProfile
	:created_at: utc-datetime в ISO-формате
	:favorited_by: список лайкнувших пользователей (список строк)
	"""

	@field_validator('author', mode='before')
	@classmethod
	def convert_to_profile(cls, value):
		"""
		в этом классовом методе провалидируйте 
		value схемой UserProfile
		"""
		return value
	

	@field_serializer('created_at')
	def convert_created_at(self, created_at: datetime) -> str:
		"""
		Сериализатор поля created_at, 
		изменений не требует
		"""
		return created_at.replace(tzinfo=UTC).isoformat().replace('+00:00', 'Z')


	@computed_field
	def favorites_count(self) -> int:
		'''
		Из этого вычисляемого поля верните 
		количество лайкнувших пользователей 
		'''
		return 0


class MultipleDreams(BaseModel):
	"""
	Схема для списка снов

	:dreams: список объектов схемы Dream
	:dreams_count: количество снов подвыборки (целое число)
	"""

	pass
