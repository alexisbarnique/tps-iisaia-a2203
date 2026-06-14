import uuid

from sqlalchemy import Enum, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.enums import CategoryEnum


class Goal(Base):
    __tablename__ = "goals"
    __table_args__ = (
        UniqueConstraint("user_id", "year", "category", name="uq_goal_user_year_category"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    category: Mapped[CategoryEnum] = mapped_column(Enum(CategoryEnum), nullable=False)
    target: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
