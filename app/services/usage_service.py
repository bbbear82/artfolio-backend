import uuid
from datetime import date, datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.usage import UsageRecord


async def check_and_increment(
    db: AsyncSession,
    user_id: uuid.UUID,
    request_type: str,
) -> int:
    """Check usage limit and increment counter.

    Returns the remaining quota. Raises ValueError if limit exceeded.
    """
    limit = (
        settings.daily_augment_limit
        if request_type == "augment"
        else settings.daily_translate_limit
    )

    today = date.today()

    result = await db.execute(
        select(UsageRecord).where(
            UsageRecord.user_id == user_id,
            UsageRecord.usage_date == today,
            UsageRecord.request_type == request_type,
        )
    )
    record = result.scalar_one_or_none()

    if record is None:
        record = UsageRecord(
            user_id=user_id,
            usage_date=today,
            request_type=request_type,
            count=0,
        )
        db.add(record)

    if record.count >= limit:
        raise ValueError(f"Daily {request_type} limit ({limit}) exceeded")

    record.count += 1
    record.updated_at = datetime.now(timezone.utc)
    await db.commit()

    return limit - record.count
