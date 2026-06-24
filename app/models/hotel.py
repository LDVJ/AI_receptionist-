from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, func, Text, DateTime, true
from ..db import Base
from datetime import datetime
from ..constants.status import FAQStatus
from sqlalchemy import Enum as SQLEnum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .users import Users


class Hotel(Base):
    __tablename__ = "hotel"

    id : Mapped[str] = mapped_column(primary_key=True, nullable=False)
    hotel_name : Mapped[str] = mapped_column(String(255) , nullable=False)
    admin_id : Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    welcome_msg : Mapped[str] = mapped_column(Text, nullable=True)
    slug : Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    created_at : Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # relationship
    faqs : Mapped[list["HotelFAQ"]] = relationship(back_populates="hotel", cascade="all, delete-orphan")
    conversation : Mapped[list["Conversations"]] = relationship(back_populates="hotel", cascade="all, delete-orphan")
    admin : Mapped["Users"] = relationship(back_populates="hotel")


class HotelFAQ(Base):
    __tablename__  = "hotel_faq"

    id : Mapped[str] = mapped_column(primary_key=True, nullable=False)
    hotel_id : Mapped[str] = mapped_column(ForeignKey("hotel.id", ondelete="CASCADE"), nullable=False)
    question : Mapped[str] = mapped_column(String(500), nullable=False)
    answer : Mapped[str] = mapped_column(Text, nullable=False)
    category : Mapped[str] = mapped_column(String(100), nullable=True)
    created_at : Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # relationship 
    hotel : Mapped["Hotel"] =  relationship(back_populates="faqs")

class Conversations(Base):
    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(primary_key=True, nullable=False)
    hotel_id : Mapped[str] = mapped_column(ForeignKey("hotel.id", ondelete="CASCADE"), nullable=False)
    guest_question : Mapped[str] = mapped_column(Text, nullable=False)
    ai_response : Mapped[str] = mapped_column(Text, nullable=False)
    was_answerable : Mapped[bool] = mapped_column(nullable=False, server_default=true())
    created_at : Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # relationship
    hotel : Mapped["Hotel"] = relationship(back_populates="conversation")
    unanswered_entry : Mapped["UnansweredQuestions | None"] = relationship(back_populates="conversation", cascade="all, delete-orphan")


class UnansweredQuestions(Base):
    __tablename__ = "unanswered_questions"

    id: Mapped[str] = mapped_column(primary_key=True, nullable=False)
    conversation_id : Mapped[str] = mapped_column(ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    status : Mapped[FAQStatus] = mapped_column(SQLEnum(FAQStatus, name = "faq_status"), nullable=False, default=FAQStatus.PENDING)
    created_at : Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # realtionship
    conversation : Mapped["Conversations"] = relationship(back_populates="unanswered_entry")

