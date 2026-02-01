import pytest

from app.services.database import database
from app.services.feedback import feedback_service
from app.services.jwt import jwt_service
from app.services.users import user_service


@pytest.fixture
async def auth_headers(async_client):
    """Create authentication headers for a test user"""
    if database.db is None:
        pytest.skip("Database not connected")

    # Clean up any existing test user
    await database.db.users.delete_many({"email": "feedback_test@example.com"})

    # Create test user - returns UserResponse object
    user = await user_service.create_user(
        email="feedback_test@example.com",
        password="testpassword123",
    )
    await user_service.verify_user(user.id)

    # Create access token
    token = jwt_service.create_access_token(user.id)

    yield {"Authorization": f"Bearer {token}"}, user.id

    # Cleanup
    if database.db is not None:
        await database.db.feedback.delete_many({})
        await database.db.users.delete_many({"email": "feedback_test@example.com"})


class TestFeedbackSubmission:
    """Tests for feedback submission endpoint"""

    @pytest.mark.asyncio
    async def test_submit_feedback_without_auth(self, async_client):
        """Test that unauthenticated users cannot submit feedback"""
        response = await async_client.post(
            "/api/feedback",
            json={
                "text": "This is a sample political text for classification testing.",
                "model_prediction": "left",
                "model_confidence": 0.873,
                "actual_label": "left",
                "is_correct": True,
            },
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_submit_feedback_thumbs_up(self, async_client, auth_headers):
        """Test submitting positive feedback (user agrees with AI)"""
        headers, _ = auth_headers

        response = await async_client.post(
            "/api/feedback",
            json={
                "text": "This is a sample political text for classification testing.",
                "model_prediction": "left",
                "model_confidence": 0.873,
                "actual_label": "left",
                "is_correct": True,
            },
            headers=headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["message"] == "Feedback submitted successfully"
        assert "created_at" in data

    @pytest.mark.asyncio
    async def test_submit_feedback_thumbs_down(self, async_client, auth_headers):
        """Test submitting negative feedback (user disagrees with AI)"""
        headers, _ = auth_headers

        response = await async_client.post(
            "/api/feedback",
            json={
                "text": "This is a sample political text for classification testing.",
                "model_prediction": "left",
                "model_confidence": 0.873,
                "actual_label": "center",
                "is_correct": False,
            },
            headers=headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["message"] == "Feedback submitted successfully"

    @pytest.mark.asyncio
    async def test_submit_feedback_thumbs_down_right(self, async_client, auth_headers):
        """Test submitting negative feedback choosing right as correct"""
        headers, _ = auth_headers

        response = await async_client.post(
            "/api/feedback",
            json={
                "text": "This is a sample political text for classification testing.",
                "model_prediction": "left",
                "model_confidence": 0.873,
                "actual_label": "right",
                "is_correct": False,
            },
            headers=headers,
        )

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_submit_feedback_invalid_consistency_thumbs_up(
        self, async_client, auth_headers
    ):
        """Test that thumbs up requires actual_label to match model_prediction"""
        headers, _ = auth_headers

        response = await async_client.post(
            "/api/feedback",
            json={
                "text": "This is a sample political text for classification testing.",
                "model_prediction": "left",
                "model_confidence": 0.873,
                "actual_label": "right",  # Should match "left" when is_correct=True
                "is_correct": True,
            },
            headers=headers,
        )

        assert response.status_code == 422
        data = response.json()
        assert "actual_label must match model_prediction" in str(data)

    @pytest.mark.asyncio
    async def test_submit_feedback_invalid_consistency_thumbs_down(
        self, async_client, auth_headers
    ):
        """Test that thumbs down requires actual_label to differ from model_prediction"""
        headers, _ = auth_headers

        response = await async_client.post(
            "/api/feedback",
            json={
                "text": "This is a sample political text for classification testing.",
                "model_prediction": "left",
                "model_confidence": 0.873,
                "actual_label": "left",  # Should differ when is_correct=False
                "is_correct": False,
            },
            headers=headers,
        )

        assert response.status_code == 422
        data = response.json()
        assert "actual_label must differ from model_prediction" in str(data)

    @pytest.mark.asyncio
    async def test_submit_feedback_invalid_label(self, async_client, auth_headers):
        """Test that invalid labels are rejected"""
        headers, _ = auth_headers

        response = await async_client.post(
            "/api/feedback",
            json={
                "text": "This is a sample political text for classification testing.",
                "model_prediction": "invalid",
                "model_confidence": 0.873,
                "actual_label": "left",
                "is_correct": False,
            },
            headers=headers,
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_submit_feedback_text_too_short(self, async_client, auth_headers):
        """Test that short text is rejected"""
        headers, _ = auth_headers

        response = await async_client.post(
            "/api/feedback",
            json={
                "text": "Short",
                "model_prediction": "left",
                "model_confidence": 0.873,
                "actual_label": "left",
                "is_correct": True,
            },
            headers=headers,
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_submit_feedback_invalid_confidence(self, async_client, auth_headers):
        """Test that invalid confidence score is rejected"""
        headers, _ = auth_headers

        response = await async_client.post(
            "/api/feedback",
            json={
                "text": "This is a sample political text for classification testing.",
                "model_prediction": "left",
                "model_confidence": 1.5,  # Invalid: > 1.0
                "actual_label": "left",
                "is_correct": True,
            },
            headers=headers,
        )

        assert response.status_code == 422


class TestFeedbackStats:
    """Tests for feedback statistics endpoint"""

    @pytest.mark.asyncio
    async def test_get_stats_empty(self, async_client):
        """Test getting stats when no feedback exists"""
        if database.db is None:
            pytest.skip("Database not connected")

        # Clean up any existing feedback
        await database.db.feedback.delete_many({})

        response = await async_client.get("/api/feedback/stats")

        assert response.status_code == 200
        data = response.json()
        assert data["total_feedback"] == 0
        assert data["correct_predictions"] == 0
        assert data["incorrect_predictions"] == 0
        assert data["accuracy_rate"] == 0.0

    @pytest.mark.asyncio
    async def test_get_stats_with_feedback(self, async_client, auth_headers):
        """Test getting stats after submitting feedback"""
        headers, _ = auth_headers

        # Clean up any existing feedback first
        if database.db is not None:
            await database.db.feedback.delete_many({})

        # Submit some feedback
        for _ in range(3):
            await async_client.post(
                "/api/feedback",
                json={
                    "text": "This is a sample political text for classification testing.",
                    "model_prediction": "left",
                    "model_confidence": 0.8,
                    "actual_label": "left",
                    "is_correct": True,
                },
                headers=headers,
            )

        await async_client.post(
            "/api/feedback",
            json={
                "text": "This is another sample political text for classification.",
                "model_prediction": "right",
                "model_confidence": 0.7,
                "actual_label": "center",
                "is_correct": False,
            },
            headers=headers,
        )

        response = await async_client.get("/api/feedback/stats")

        assert response.status_code == 200
        data = response.json()
        assert data["total_feedback"] == 4
        assert data["correct_predictions"] == 3
        assert data["incorrect_predictions"] == 1
        assert data["accuracy_rate"] == 0.75


class TestFeedbackService:
    """Unit tests for feedback service"""

    @pytest.mark.asyncio
    async def test_create_feedback_with_user(self, async_client, auth_headers):
        """Test creating feedback with user ID"""
        _, user_id = auth_headers

        feedback = await feedback_service.create_feedback(
            text="Test political content for the classifier.",
            model_prediction="center",
            model_confidence=0.55,
            actual_label="center",
            is_correct=True,
            user_id=user_id,
        )

        assert feedback["text"] == "Test political content for the classifier."
        assert feedback["model_prediction"] == "center"
        assert feedback["is_correct"] is True
        assert feedback["user_id"] is not None
        assert "_id" in feedback

    @pytest.mark.asyncio
    async def test_get_recent_feedback(self, async_client, auth_headers):
        """Test getting recent feedback entries"""
        _, user_id = auth_headers

        # Clean up first
        if database.db is not None:
            await database.db.feedback.delete_many({})

        # Create some feedback
        for i in range(5):
            await feedback_service.create_feedback(
                text=f"Political text sample number {i} for testing purposes.",
                model_prediction="left",
                model_confidence=0.8,
                actual_label="left",
                is_correct=True,
                user_id=user_id,
            )

        recent = await feedback_service.get_recent_feedback(limit=3)

        assert len(recent) == 3
        # Most recent should be first
        assert "4" in recent[0]["text"]

    @pytest.mark.asyncio
    async def test_get_incorrect_feedback(self, async_client, auth_headers):
        """Test getting incorrect prediction feedback"""
        _, user_id = auth_headers

        # Clean up first
        if database.db is not None:
            await database.db.feedback.delete_many({})

        # Create mixed feedback
        await feedback_service.create_feedback(
            text="Correct prediction sample text for testing purposes.",
            model_prediction="left",
            model_confidence=0.8,
            actual_label="left",
            is_correct=True,
            user_id=user_id,
        )
        await feedback_service.create_feedback(
            text="Incorrect prediction sample text for testing purposes.",
            model_prediction="left",
            model_confidence=0.6,
            actual_label="right",
            is_correct=False,
            user_id=user_id,
        )

        incorrect = await feedback_service.get_incorrect_feedback()

        assert len(incorrect) == 1
        assert incorrect[0]["is_correct"] is False
        assert incorrect[0]["actual_label"] == "right"

    @pytest.mark.asyncio
    async def test_get_user_feedback(self, async_client, auth_headers):
        """Test getting feedback for a specific user"""
        _, user_id = auth_headers

        # Clean up first
        if database.db is not None:
            await database.db.feedback.delete_many({})

        # Create feedback for this user
        for i in range(3):
            await feedback_service.create_feedback(
                text=f"User feedback sample {i} for testing purposes here.",
                model_prediction="center",
                model_confidence=0.7,
                actual_label="center",
                is_correct=True,
                user_id=user_id,
            )

        user_feedback = await feedback_service.get_user_feedback(user_id)

        assert len(user_feedback) == 3
        for fb in user_feedback:
            assert fb["user_id"] == user_id
