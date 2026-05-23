import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.apple import verify_apple_identity_token
from app.auth.jwt import create_session_token
from app.models.base import get_db
from app.models.user import User
from app.schemas.auth import AppleAuthRequest, AuthResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/apple", response_model=AuthResponse)
async def auth_apple(
    request: AppleAuthRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        claims = await verify_apple_identity_token(request.identity_token)
    except Exception as e:
        logger.warning("Apple token verification failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Apple identity token",
        )

    apple_sub = claims["sub"]

    result = await db.execute(select(User).where(User.apple_sub == apple_sub))
    user = result.scalar_one_or_none()

    if user is None:
        user = User(
            apple_sub=apple_sub,
            email=request.email or claims.get("email"),
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    else:
        user.last_login_at = datetime.now(timezone.utc)
        await db.commit()

    token = create_session_token(str(user.id))
    return AuthResponse(token=token, user_id=str(user.id))
