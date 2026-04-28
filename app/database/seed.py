import logging
import os
import sys
from random import choice

from faker import Faker
from sqlalchemy import delete, select

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from app.database import Base, SessionLocal, engine, models
from app.security import get_password_hash

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main() -> None:
	Base.metadata.create_all(bind=engine)

	db = SessionLocal()

	logger.info('Cleanup')
	db.execute(delete(models.Dream))
	db.execute(delete(models.User))

	fake = Faker()

	logger.info('Generate 50 users')

	password = get_password_hash('password')

	for _ in range(50):
		user = models.User(
			username=fake.name(),
			password=password,
		)
		db.add(user)

	db.commit()

	users = (db.scalars(select(models.User))).unique().all()

	logger.info('Generate 500 dreams')

	for _ in range(500):
		dream = models.Dream(
			description=fake.paragraph(),
		)

		dream.author = choice(users)
		db.add(dream)

	db.commit()


if __name__ == '__main__':
	main()
