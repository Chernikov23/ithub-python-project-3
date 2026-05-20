from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import models
from app.dependencies import get_current_active_user, get_db
from app.schema import Dream, DreamCreate, DreamUpdate, MultipleDreams
from app.services import dreams_service

router = APIRouter(prefix='/dreams')


@router.post('', response_model=Dream, status_code=status.HTTP_201_CREATED)
def create_dream(
	new_dream_payload: DreamCreate,
	session: Session = Depends(get_db),
	current_user: models.User = Depends(get_current_active_user),
) -> Dream:
	dream = dreams_service.create(session=session, new_dream=new_dream_payload, author=current_user)
	return dream


@router.get('', response_model=MultipleDreams)
def get_dreams(
	page: int = 1,
	per_page: int = 10,
	mine_only: bool = False,
	session: Session = Depends(get_db),
	current_user: models.User = Depends(get_current_active_user),
) -> MultipleDreams:
	dreams, total_count = dreams_service.get_all_dreams(
		session=session,
		page=page,
		per_page=per_page,
		author_id=current_user.id if mine_only else None,
	)
	# Явное преобразование для mypy
	dreams_schema_list: list[Dream] = [Dream.model_validate(d) for d in dreams]

	return MultipleDreams(dreams=dreams_schema_list, total_count=total_count)


@router.get('/{id}', response_model=Dream)
def get_dream_by_id(
	id: int,
	session: Session = Depends(get_db),
	current_user: models.User = Depends(get_current_active_user),
) -> Dream:
	dream = dreams_service.get_by_id(session=session, id=id)
	if not dream:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Dream not found')
	if dream.author_id != current_user.id:
		raise HTTPException(
			status_code=status.HTTP_403_FORBIDDEN, detail='Not authorized to access this dream'
		)
	return dream


@router.put('/{id}', response_model=Dream)
def update_dream(
	id: int,
	updated_dream_payload: DreamUpdate,
	session: Session = Depends(get_db),
	current_user: models.User = Depends(get_current_active_user),
) -> Dream:
	dream = dreams_service.get_by_id(session=session, id=id)
	if not dream:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Dream not found')
	if dream.author_id != current_user.id:
		raise HTTPException(
			status_code=status.HTTP_403_FORBIDDEN, detail='Not authorized to update this dream'
		)
	updated_dream = dreams_service.update(
		session=session, dream_id=id, updated_dream_payload=updated_dream_payload
	)
	return updated_dream


@router.delete('/{id}')  # response_model=None по умолчанию
def delete_dream(
	id: int,
	session: Session = Depends(get_db),
	current_user: models.User = Depends(get_current_active_user),
) -> None:  # <-- Аннотация возвращаемого типа
	dream = dreams_service.get_by_id(session=session, id=id)
	if not dream:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Dream not found')
	if dream.author_id != current_user.id:
		raise HTTPException(
			status_code=status.HTTP_403_FORBIDDEN, detail='Not authorized to delete this dream'
		)
	dreams_service.delete(session=session, dream_id=id)
