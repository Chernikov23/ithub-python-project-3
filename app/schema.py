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
    token_type: Literal["bearer"] = "bearer"


class UserCreate(BaseModel):
    """
    TODO
    Схема данных для создания пользователя

    :username: строка длиной не менее 2 символов
    :password: строка длиной не менее 8 символов
    """

    username: str = Field(..., min_length=2, description="Имя пользователя")
    password: str = Field(..., min_length=8, description="Пароль пользователя")


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

    @field_serializer("created_at")
    def serialize_created_at(self, created_at: datetime) -> str:
        return created_at.isoformat()


class NewDream(BaseModel):
    """
    TODO
    Схема данных для создания нового сна

    :description: строка длиной не менее 5
    """

    description: str = Field(..., min_length=5, description="Описание сна")


class MultipleDreams(BaseModel):
    """
    :dreams: список Dream-ов
    :dreams_count: количество снов в подвыборке, целое число
    """

    dreams: list[Dream]
    dreams_count: int
