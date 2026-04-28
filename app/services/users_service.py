from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import models


def get_by_username(*, session: Session, username: str) -> models.User | None:
	return session.scalar(select(models.User).filter_by(username=username))
