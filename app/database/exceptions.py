import sqlite3


class DuplicateDreamException(sqlite3.IntegrityError):
	def __init__(self):
		super().__init__('Автор уже публиковал этот сон')

