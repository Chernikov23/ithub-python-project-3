from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel as PBaseModel
from pydantic import ConfigDict, Field, computed_field, field_serializer, field_validator


class BaseModel(PBaseModel):
	model_config = ConfigDict(populate_by_name=True, from_attributes=True)


class UserToken(BaseModel):
	access_token: str
	token_type: Literal['bearer'] = 'bearer'


class Username(BaseModel):
	username: str = Field(min_length=1)


class UserCreate(BaseModel):
	username: str = Field(min_length=1)
	password: str = Field(min_length=5)
	bio: str | None = None


class UserUpdate(BaseModel):
	bio: str | None = None


class UserProfile(BaseModel):
	username: str
	bio: str | None = None
	is_superuser: bool = Field(default=False, exclude=True)


class NewDream(BaseModel):
	description: str = Field(min_length=5)


class Dream(BaseModel):
	id: int
	description: str
	author: UserProfile
	created_at: datetime
	favorited_by: list[str] = []

	@field_validator('author', mode='before')
	@classmethod
	def convert_to_profile(cls, value: Any) -> UserProfile:
		if isinstance(value, UserProfile):
			return value
		return UserProfile.model_validate(value)

	@field_validator('favorited_by', mode='before')
	@classmethod
	def convert_favorited_by(cls, value: Any) -> list[str]:
		usernames = []
		for item in value:
			if isinstance(item, str):
				usernames.append(item)
			else:
				usernames.append(item.username)
		return usernames

	@field_serializer('created_at')
	def convert_created_at(self, created_at: datetime) -> str:
		return created_at.replace(tzinfo=UTC).isoformat().replace('+00:00', 'Z')

	@computed_field
	def favorites_count(self) -> int:
		return len(self.favorited_by)


class MultipleDreams(BaseModel):
	dreams: list[Dream]
	dreams_count: int
