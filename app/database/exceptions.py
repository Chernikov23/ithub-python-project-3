import sqlite3


class DuplicateDatabaseException(sqlite3.IntegrityError):
	def __init__(self, message: str | None = "Запись уже существует"):
		super().__init__(message)


class NotFoundDatabaseException(sqlite3.IntegrityError):
	def __init__(self, message: str | None = "Запись не найдена"):
		super().__init__(message)

