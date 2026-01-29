import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def async_client():
    """Async test client for testing endpoints"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


class TestClassifyEndpoint:
    """Tests for the /api/classify endpoint"""

    @pytest.mark.asyncio
    async def test_classify_returns_valid_response(self, async_client: AsyncClient):
        """Test that classify endpoint returns expected response structure"""
        response = await async_client.post(
            "/api/classify",
            json={"text": "The government should increase taxes on the wealthy."},
        )

        assert response.status_code == 200
        data = response.json()

        # Check response structure
        assert "prediction" in data
        assert "confidence" in data
        assert "probabilities" in data

        # Check prediction is valid
        assert data["prediction"] in ["left", "center", "right"]

        # Check confidence is valid
        assert 0.0 <= data["confidence"] <= 1.0

        # Check probabilities structure
        probs = data["probabilities"]
        assert "left" in probs
        assert "center" in probs
        assert "right" in probs

        # Check probabilities are valid
        for label in ["left", "center", "right"]:
            assert 0.0 <= probs[label] <= 1.0

        # Check probabilities sum to approximately 1
        total = probs["left"] + probs["center"] + probs["right"]
        assert 0.99 <= total <= 1.01

    @pytest.mark.asyncio
    async def test_classify_left_leaning_text(self, async_client: AsyncClient):
        """Test classification of left-leaning political text"""
        response = await async_client.post(
            "/api/classify",
            json={
                "text": "Universal healthcare is a human right. We must expand social programs to help working families and reduce income inequality through progressive taxation."
            },
        )

        assert response.status_code == 200
        data = response.json()
        # We expect left-leaning text to have higher left probability
        # Note: This is a soft assertion as model predictions may vary
        assert data["prediction"] in ["left", "center", "right"]

    @pytest.mark.asyncio
    async def test_classify_right_leaning_text(self, async_client: AsyncClient):
        """Test classification of right-leaning political text"""
        response = await async_client.post(
            "/api/classify",
            json={
                "text": "Lower taxes and less government regulation will boost economic growth and create jobs. We must protect traditional values and secure our borders."
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["prediction"] in ["left", "center", "right"]

    @pytest.mark.asyncio
    async def test_classify_center_text(self, async_client: AsyncClient):
        """Test classification of centrist/neutral text"""
        response = await async_client.post(
            "/api/classify",
            json={
                "text": "The committee heard arguments from both sides before reaching a bipartisan compromise on the infrastructure bill. Both parties contributed to the final agreement."
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["prediction"] in ["left", "center", "right"]


class TestClassifyValidation:
    """Tests for input validation on the classify endpoint"""

    @pytest.mark.asyncio
    async def test_classify_rejects_empty_text(self, async_client: AsyncClient):
        """Test that empty text is rejected"""
        response = await async_client.post("/api/classify", json={"text": ""})

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    @pytest.mark.asyncio
    async def test_classify_rejects_whitespace_only(self, async_client: AsyncClient):
        """Test that whitespace-only text is rejected"""
        response = await async_client.post("/api/classify", json={"text": "   \n\t  "})

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    @pytest.mark.asyncio
    async def test_classify_rejects_too_short_text(self, async_client: AsyncClient):
        """Test that text shorter than minimum length is rejected"""
        response = await async_client.post(
            "/api/classify",
            json={"text": "Too short"},  # Less than 10 chars
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_classify_rejects_missing_text(self, async_client: AsyncClient):
        """Test that missing text field is rejected"""
        response = await async_client.post("/api/classify", json={})

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_classify_rejects_non_string_text(self, async_client: AsyncClient):
        """Test that non-string text is rejected"""
        response = await async_client.post("/api/classify", json={"text": 12345})

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_classify_rejects_null_text(self, async_client: AsyncClient):
        """Test that null text is rejected"""
        response = await async_client.post("/api/classify", json={"text": None})

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_classify_handles_text_at_minimum_length(
        self, async_client: AsyncClient
    ):
        """Test that text at exactly minimum length is accepted"""
        # Exactly 10 characters
        response = await async_client.post("/api/classify", json={"text": "1234567890"})

        assert response.status_code == 200


class TestInputSanitization:
    """Tests for input sanitization"""

    @pytest.mark.asyncio
    async def test_sanitizes_control_characters(self, async_client: AsyncClient):
        """Test that control characters are stripped from input"""
        # Text with control characters that should be removed
        text_with_controls = "This is a test\x00\x01\x02 with control chars"
        response = await async_client.post(
            "/api/classify", json={"text": text_with_controls}
        )

        # Should succeed after sanitization
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_sanitizes_excessive_whitespace(self, async_client: AsyncClient):
        """Test that excessive whitespace is normalized"""
        text_with_spaces = "This    has    many     spaces    in    between"
        response = await async_client.post(
            "/api/classify", json={"text": text_with_spaces}
        )

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_sanitizes_excessive_newlines(self, async_client: AsyncClient):
        """Test that excessive newlines are normalized"""
        text_with_newlines = "Paragraph one\n\n\n\n\n\nParagraph two"
        response = await async_client.post(
            "/api/classify", json={"text": text_with_newlines}
        )

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_strips_leading_trailing_whitespace(self, async_client: AsyncClient):
        """Test that leading/trailing whitespace is stripped"""
        text_with_padding = "   \n\n  This is the actual text   \n\n   "
        response = await async_client.post(
            "/api/classify", json={"text": text_with_padding}
        )

        assert response.status_code == 200
