from pydantic import BaseModel


class AppleAuthRequest(BaseModel):
    identity_token: str
    email: str | None = None


class AuthResponse(BaseModel):
    token: str
    user_id: str
