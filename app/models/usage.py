import uuid
from datetime import date, datetime, timezone

from sqlalchemy import String, Integer, Date, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class UsageRecord(Base):
    __tablename__ = "usage_records"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    usage_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    request_type: Mapped[str] = mapped_column(String(20), nullable=False)  # "augment" or "translate"
    count: Mapped[int] = mapped_column(Integer, default=0)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
