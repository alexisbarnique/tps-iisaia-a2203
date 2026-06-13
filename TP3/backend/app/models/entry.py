import uuid

from sqlalchemy import String, Integer, Date, Text, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.enums import CategoryEnum, PlaceTypeEnum


class Entry(Base):
    __tablename__ = "entries"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    category: Mapped[CategoryEnum] = mapped_column(Enum(CategoryEnum), nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    date = mapped_column(Date, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())

    # movie_series, book, place
    rating: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # movie_series, book
    saga_name: Mapped[str | None] = mapped_column(String, nullable=True)
    saga_part: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # movie_series only
    season_number: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # city, place
    country: Mapped[str | None] = mapped_column(String, nullable=True)

    # place only
    city: Mapped[str | None] = mapped_column(String, nullable=True)
    place_type: Mapped[PlaceTypeEnum | None] = mapped_column(Enum(PlaceTypeEnum), nullable=True)
