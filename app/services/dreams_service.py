from collections.abc import Sequence
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload
from app import schema
from app.database import models
from app.database.exceptions import DuplicateDatabaseException

def get_by_id(session: Session, id: int) -> models.Dream | None:
    stmt = select(models.Dream).options(joinedload(models.Dream.author)).where(models.Dream.id == id)
    return session.execute(stmt).scalars().unique().first()

def get_all_dreams(session: Session, page: int, per_page: int, author_name: str | None = None) -> tuple[Sequence[models.Dream], int]:
    query = select(models.Dream).options(joinedload(models.Dream.author))
    if author_name:
        query = query.where(models.Dream.author_id.ilike(f"%{author_name}%"))
    
    total_count = session.query(func.count(models.Dream.id))
    if author_name:
        total_count = total_count.filter(models.Dream.author_id.ilike(f"%{author_name}%"))
    total_count = total_count.scalar() or 0

    results = session.execute(query.offset((page-1)*per_page).limit(per_page)).scalars().unique().all()
    return results, total_count

def create(session: Session, new_dream: schema.DreamCreate, author: models.User) -> models.Dream:
    db_dream = models.Dream(description=new_dream.description, author_id=author.username)
    try:
        session.add(db_dream)
        session.commit()
        session.refresh(db_dream)
        return db_dream
    except IntegrityError:
        session.rollback()
        raise DuplicateDatabaseException(message="Duplicate dream")

def update(session: Session, dream_id: int, updated_dream_payload: schema.DreamUpdate) -> models.Dream:
    dream = session.get(models.Dream, dream_id)
    if dream:
        dream.description = updated_dream_payload.description
        session.commit()
        session.refresh(dream)
    return dream 

def delete(session: Session, dream_id: int) -> None:
    dream = session.get(models.Dream, dream_id)
    if dream:
        session.delete(dream)
        session.commit()