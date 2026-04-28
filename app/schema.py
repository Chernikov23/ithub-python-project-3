from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel as PBaseModel
from pydantic import ConfigDict, Field, computed_field, field_serializer, field_validator


class BaseModel(PBaseModel):
	model_config = ConfigDict(
		populate_by_name=True, from_attributes=True
	)


class Username(BaseModel):
	username: str


class UserCreate(BaseModel):
	username: str = Field(min_length=1)
	password: str = Field(min_length=8)
	bio: str | None = None


class UserUpdate(BaseModel):
	bio: str | None = None


class UserProfile(BaseModel):
	username: str
	bio: str | None = None


class UserToken(BaseModel):
	access_token: str
	token_type: Literal['bearer'] = 'bearer'


class Dream(BaseModel):
	id: int
	description: str
	author: UserProfile
	created_at: datetime
	favorited_by: list[str]

	@field_validator('favorited_by', mode='before')
	@classmethod
	def convert_to_profiles(cls, value):
		return [Username.model_validate(user).username for user in value]

	@field_validator('author', mode='before')
	@classmethod
	def convert_to_profile(cls, value):
		return UserProfile.model_validate(value)

	@field_serializer('created_at')
	def convert_created_at(self, created_at: datetime) -> str:
		return created_at.replace(tzinfo=UTC).isoformat().replace('+00:00', 'Z')

	@computed_field
	def favorites_count(self) -> int:
		return len(self.favorited_by)


class NewDream(BaseModel):
	description: str = Field(min_length=5)


class MultipleDreams(BaseModel):
	dreams: list[Dream]
	dreams_count: int
