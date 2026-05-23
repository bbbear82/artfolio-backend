import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.auth.jwt import decode_session_token

_bearer_scheme = HTTPBearer()


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
) -> uuid.UUID:
    try:
        payload = decode_session_token(credentials.credentials)
        return uuid.UUID(payload["sub"])
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
