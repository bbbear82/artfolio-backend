import httpx
import jwt
from jwt import PyJWKClient

from app.config import settings

APPLE_JWKS_URL = "https://appleid.apple.com/auth/keys"
APPLE_ISSUER = "https://appleid.apple.com"

_jwks_client = PyJWKClient(APPLE_JWKS_URL, cache_keys=True)


async def verify_apple_identity_token(identity_token: str) -> dict:
    """Verify an Apple identity token and return the decoded claims.

    Raises jwt.PyJWTError on any verification failure.
    """
    signing_key = _jwks_client.get_signing_key_from_jwt(identity_token)

    decoded = jwt.decode(
        identity_token,
        signing_key.key,
        algorithms=["RS256"],
        audience=settings.apple_bundle_id,
        issuer=APPLE_ISSUER,
    )

    return decoded
