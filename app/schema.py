from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel as PBaseModel
from pydantic import ConfigDict, Field, field_serializer


class BaseModel(PBaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)


class UserToken(BaseModel):

    access_token: str
    token_type: Literal['bearer'] = 'bearer'


class UserCreate(BaseModel):

    username: str = Field(..., min_length=2)
    password: str = Field(..., min_length=8)


class UserProfile(BaseModel):

    username: str


class Dream(BaseModel):

    id: int
    description: str
    author: str
    created_at: datetime

    @field_serializer('created_at')
    def serialize_created_at(self, created_at: datetime) -> str:
        return created_at.isoformat()


class NewDream(BaseModel):

    description: str = Field(..., min_length=5)


class MultipleDreams(BaseModel):

    dreams: list[Dream]
    dreams_count: int