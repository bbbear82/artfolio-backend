import uuid
from unittest.mock import patch, AsyncMock

import pytest
import pytest_asyncio

from app.auth.jwt import create_session_token, decode_session_token


class TestJWT:
    def test_create_and_decode_token(self):
        user_id = str(uuid.uuid4())
        token = create_session_token(user_id)
        decoded = decode_session_token(token)
        assert decoded["sub"] == user_id

    def test_invalid_token_raises(self):
        import jwt
        with pytest.raises(jwt.PyJWTError):
            decode_session_token("invalid.token.here")


class TestAppleAuth:
    @pytest.mark.asyncio
    async def test_apple_auth_creates_user(self, client, db_session):
        fake_claims = {"sub": "apple-user-123", "email": "test@example.com"}

        with patch("app.routers.auth_router.verify_apple_identity_token", new_callable=AsyncMock) as mock_verify:
            mock_verify.return_value = fake_claims
            response = await client.post("/auth/apple", json={
                "identity_token": "fake-token",
                "email": "test@example.com",
            })

        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "user_id" in data

    @pytest.mark.asyncio
    async def test_apple_auth_returns_existing_user(self, client, db_session):
        fake_claims = {"sub": "apple-user-456"}

        with patch("app.routers.auth_router.verify_apple_identity_token", new_callable=AsyncMock) as mock_verify:
            mock_verify.return_value = fake_claims

            resp1 = await client.post("/auth/apple", json={"identity_token": "tok1"})
            resp2 = await client.post("/auth/apple", json={"identity_token": "tok2"})

        assert resp1.json()["user_id"] == resp2.json()["user_id"]

    @pytest.mark.asyncio
    async def test_apple_auth_invalid_token(self, client):
        with patch("app.routers.auth_router.verify_apple_identity_token", new_callable=AsyncMock) as mock_verify:
            mock_verify.side_effect = Exception("Invalid token")
            response = await client.post("/auth/apple", json={"identity_token": "bad"})

        assert response.status_code == 401
