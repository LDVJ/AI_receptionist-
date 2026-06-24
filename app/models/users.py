from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, func
from app.db import Base
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .hotel import Hotel, HotelFAQ, UnansweredQuestions, Conversations


class Users(Base):
    __tablename__ = "users"

    id : Mapped[str] = mapped_column(primary_key=True, nullable=False)
    name : Mapped[str] = mapped_column(String(100),nullable=False)
    email : Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    hash_password : Mapped[str] = mapped_column(String(255), nullable=False)
    created_at : Mapped[datetime] = mapped_column(DateTime(timezone=True),nullable=False, server_default=func.now())

    hotel : Mapped["Hotel"] = relationship(back_populates="admin")