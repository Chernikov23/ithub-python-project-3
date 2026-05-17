from sqlite3 import Cursor
from app import schema


def get_by_username(*, cursor: Cursor, username: str) -> schema.UserProfile | None:
    """
    :cursor: курсор подключения к базе данных
    :username: уникальный юзернейм пользователя

    Запрашивает пользователя из базы данных.
    Если пользователь не найден, возвращает None.
    Иначе - возвращает запись согласно схеме.
    """
    cursor.execute(
        'SELECT username FROM users WHERE username = ?',
        (username,)
    )
    result = cursor.fetchone()

    if not result:
        return None

    return schema.UserProfile(username=result[0])
