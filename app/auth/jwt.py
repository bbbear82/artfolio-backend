from datetime import datetime, timedelta, timezone

import jwt as pyjwt

from app.config import settings

ALGORITHM = "HS256"
TOKEN_EXPIRY_DAYS = 30


def create_session_token(user_id: str) -> str:
    payload = {
        "sub": user_id,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(days=TOKEN_EXPIRY_DAYS),
    }
    return pyjwt.encode(payload, settings.jwt_secret, algorithm=ALGORITHM)


def decode_session_token(token: str) -> dict:
    """Decode and verify a session JWT. Raises pyjwt.PyJWTError on failure."""
    return pyjwt.decode(token, settings.jwt_secret, algorithms=[ALGORITHM])
