from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import models
from app.api.dependencies import get_current_active_user, get_db
from app.schema import Dream, DreamCreate, DreamUpdate, MultipleDreams
from app.services import dreams_service

dreams_router = APIRouter(prefix='/dreams')

@dreams_router.post('', response_model=Dream, status_code=status.HTTP_201_CREATED)
def create_dream(
    new_dream_payload: DreamCreate,
    session: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
) -> models.Dream:
    return dreams_service.create(session=session, new_dream=new_dream_payload, author=current_user)

@dreams_router.get('', response_model=MultipleDreams)
def get_dreams(
    page: int = 1,
    per_page: int = 10,
    author: str | None = None,
    session: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
) -> MultipleDreams:
    dreams, total_count = dreams_service.get_all_dreams(
        session=session, page=page, per_page=per_page, author_name=author
    )
    return MultipleDreams(dreams=[Dream.model_validate(d) for d in dreams], total_count=total_count)

@dreams_router.get('/{id}', response_model=Dream)
def get_dream_by_id(
    id: int,
    session: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
) -> models.Dream:
    dream = dreams_service.get_by_id(session=session, id=id)
    if not dream:
        raise HTTPException(status_code=404, detail='Dream not found')
    return dream

@dreams_router.put('/{id}', response_model=Dream)
def update_dream(
    id: int,
    updated_dream_payload: DreamUpdate,
    session: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
) -> models.Dream:
    dream = dreams_service.get_by_id(session=session, id=id)
    if not dream:
        raise HTTPException(status_code=404, detail="Dream not found")
    if dream.author_id != current_user.username:
        raise HTTPException(status_code=403, detail="Forbidden")
    return dreams_service.update(session=session, dream_id=id, updated_dream_payload=updated_dream_payload)

@dreams_router.delete('/{id}', status_code=204)
def delete_dream(
    id: int,
    session: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
) -> None:
    dream = dreams_service.get_by_id(session=session, id=id)
    if not dream:
        raise HTTPException(status_code=404, detail="Dream not found")
    if dream.author_id != current_user.username:
        raise HTTPException(status_code=403, detail="Forbidden")
    dreams_service.delete(session=session, dream_id=id)