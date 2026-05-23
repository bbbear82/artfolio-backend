import uuid
from unittest.mock import patch, AsyncMock

import pytest
import pytest_asyncio

from app.models.user import User


@pytest_asyncio.fixture
async def seeded_user(db_session, test_user_id):
    user = User(id=test_user_id, apple_sub=f"apple-{test_user_id}")
    db_session.add(user)
    await db_session.commit()
    return user


class TestAugmentEndpoint:
    @pytest.mark.asyncio
    async def test_augment_description(self, client, auth_headers, seeded_user):
        mock_response = {"description": "A beautiful watercolor painting."}

        with patch("app.routers.augment_router.call_augment", new_callable=AsyncMock) as mock_call:
            mock_call.return_value = mock_response
            response = await client.post("/api/augment", json={
                "studio_text": "Students explored watercolor techniques.",
                "terms": ["watercolor", "wash"],
                "title": "Spring Flowers",
                "mode": "description",
            }, headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "A beautiful watercolor painting."
        assert "X-Quota-Remaining" in response.headers

    @pytest.mark.asyncio
    async def test_augment_all_mode(self, client, auth_headers, seeded_user):
        mock_response = {
            "description": "A study in impasto technique.",
            "definitions": {"impasto": "Thick paint application"},
            "portfolio_statement": "This piece demonstrates growth.",
        }

        with patch("app.routers.augment_router.call_augment", new_callable=AsyncMock) as mock_call:
            mock_call.return_value = mock_response
            response = await client.post("/api/augment", json={
                "studio_text": "Lesson on impasto.",
                "terms": ["impasto"],
                "mode": "all",
            }, headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["description"] is not None
        assert data["definitions"] is not None
        assert data["portfolio_statement"] is not None

    @pytest.mark.asyncio
    async def test_augment_unauthorized(self, client):
        response = await client.post("/api/augment", json={
            "studio_text": "test",
            "mode": "description",
        })
        assert response.status_code in (401, 403)

    @pytest.mark.asyncio
    async def test_augment_rate_limit(self, client, auth_headers, seeded_user):
        mock_response = {"description": "test"}

        with patch("app.routers.augment_router.call_augment", new_callable=AsyncMock) as mock_call:
            mock_call.return_value = mock_response

            for i in range(10):
                resp = await client.post("/api/augment", json={
                    "studio_text": "test", "mode": "description",
                }, headers=auth_headers)
                assert resp.status_code == 200

            resp = await client.post("/api/augment", json={
                "studio_text": "test", "mode": "description",
            }, headers=auth_headers)
            assert resp.status_code == 429


class TestTranslateEndpoint:
    @pytest.mark.asyncio
    async def test_translate_success(self, client, auth_headers, seeded_user):
        mock_response = {
            "description": "Una hermosa pintura.",
            "portfolio_statement": None,
            "definitions": {"watercolor": "acuarela: pintura con agua"},
        }

        with patch("app.routers.augment_router.call_translate", new_callable=AsyncMock) as mock_call:
            mock_call.return_value = mock_response
            response = await client.post("/api/translate", json={
                "description": "A beautiful painting.",
                "term_definitions": {"watercolor": "Painting with water-based pigments"},
                "target_language": "es",
            }, headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["translated_description"] == "Una hermosa pintura."

    @pytest.mark.asyncio
    async def test_translate_empty_body_rejected(self, client, auth_headers, seeded_user):
        response = await client.post("/api/translate", json={
            "target_language": "zh-Hans",
        }, headers=auth_headers)
        assert response.status_code == 400


class TestHealthEndpoint:
    @pytest.mark.asyncio
    async def test_health(self, client):
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
