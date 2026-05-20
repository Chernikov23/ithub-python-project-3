from sqlite3 import Cursor

from app import schema


def get_by_username(*, cursor: Cursor, username: str) -> schema.UserProfile | None:
    row = cursor.execute(
        "SELECT username FROM users WHERE username = ?",
        (username,),
    ).fetchone()

    if row is None:
        return None

    return schema.UserProfile(username=row[0])