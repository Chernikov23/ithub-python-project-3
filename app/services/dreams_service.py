import sqlite3
from collections.abc import Sequence

from sqlalchemy import Select
from sqlalchemy.orm import Session

from app import schema
from app.database import models


def get_by_id(session: Session, id: int) -> models.Dream | None:
	pass


def get_list(
	*,
	session: Session,
	limit: int,
	offset: int,
	author: str | None = None,
	search: str | None = None,
) -> tuple[Sequence[models.Dream], int]:
	pass


def get_paginated_list(
	*, session: Session, limit: int, offset: int, query: Select[tuple[models.Dream]]
) -> tuple[Sequence[models.Dream], int]:
	pass


def create(*, session: Session, new_dream: schema.NewDream, author: models.User) -> models.Dream:
	pass


def delete(*, session: Session, dream_id: int) -> None:
	pass
