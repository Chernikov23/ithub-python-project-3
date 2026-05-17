from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Dream(Base):
    __tablename__ = "dreams"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    author_id: Mapped[str] = mapped_column(
        String, ForeignKey("users.username"), nullable=False
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, nullable=False
    )

    author: Mapped["User"] = relationship(
        "User", back_populates="dreams", lazy="joined"
    )

    __table_args__ = (
        UniqueConstraint("author_id", "description", name="uq_author_description"),
    )


class User(Base):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    password: Mapped[str | None] = mapped_column(String, nullable=False)

    dreams: Mapped[list[Dream]] = relationship(
        "Dream", back_populates="author", lazy="joined"
    )
