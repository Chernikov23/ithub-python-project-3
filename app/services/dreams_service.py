from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app import schema
from app.database import models
from app.database.exceptions import DuplicateDatabaseException


def get_by_id(session: Session, id: int) -> models.Dream | None:
	"""
	Возвращает информацию обо сне, подгружая данные об авторе.
	Добавлен .unique() для предотвращения ошибки InvalidRequestError.
	"""
	stmt = (
		select(models.Dream).options(joinedload(models.Dream.author)).where(models.Dream.id == id)
	)
	# .unique() обязателен при использовании joinedload в SQLAlchemy 2.0+
	result = session.execute(stmt).scalars().unique().first()
	return result


def get_list(
	*,
	session: Session,
	limit: int,
	offset: int,
	author: str | None = None,
) -> tuple[Sequence[models.Dream], int]:
	"""
	Получает пагинированный список снов с фильтрацией по автору.
	"""
	# Базовый запрос с подгрузкой автора
	query = (
		select(models.Dream)
		.options(joinedload(models.Dream.author))
		.order_by(models.Dream.created_at.desc())
	)

	# Если передан автор, фильтруем через связь
	if author:
		query = query.where(models.Dream.author.has(models.User.username.ilike(f'%{author}%')))

	# Считаем общее количество подходящих записей
	count_stmt = select(func.count()).select_from(query.subquery())
	total_count = session.execute(count_stmt).scalar() or 0

	# Получаем пагинированные результаты
	# .unique() здесь также критически важен
	results = session.execute(query.offset(offset).limit(limit)).scalars().unique().all()

	return results, total_count


def create(
	*, session: Session, new_dream: schema.NewDream, author: schema.UserProfile
) -> models.Dream:
	"""
	Добавляет новый сон. Если автор и описание совпадают (дубликат),
	выбрасывает DuplicateDatabaseException.
	"""
	db_dream = models.Dream(description=new_dream.description, author_id=author.username)

	try:
		session.add(db_dream)
		session.commit()
		session.refresh(db_dream)
		return db_dream
	except IntegrityError:
		session.rollback()
		raise DuplicateDatabaseException(message='Пользователь уже добавлял этот сон')


def delete(*, session: Session, dream_id: int) -> None:
	"""
	Удаляет сон из базы данных по его идентификатору.
	"""
	dream = session.get(models.Dream, dream_id)
	if dream:
		session.delete(dream)
		session.commit()
