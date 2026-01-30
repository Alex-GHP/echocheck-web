from unittest.mock import MagicMock, patch

import pytest
from httpx import AsyncClient

from app.services.database import database


@pytest.fixture
def unique_email():
    """Generate a unique email for each test"""
    import uuid

    return f"test-{uuid.uuid4().hex[:8]}@example.com"


@pytest.fixture
def mock_email_service():
    """Mock the email service to not actually send emails"""
    with patch("app.services.verification.get_email_service") as mock:
        mock_service = MagicMock()
        mock_service.send_verification_code.return_value = True
        mock_service.send_welcome_email.return_value = True
        mock.return_value = mock_service
        yield mock_service


class TestRegistrationFlow:
    """Tests for 2FA registration flow"""

    @pytest.mark.asyncio
    async def test_register_init_success(
        self, async_client: AsyncClient, unique_email, mock_email_service
    ):
        """Test initiating registration sends verification code"""
        if database.db is None:
            pytest.skip("Database not connected")

        response = await async_client.post(
            "/api/auth/register",
            json={
                "email": unique_email,
                "password": "securepassword123",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["email"] == unique_email.lower()
        assert "expires_in_minutes" in data
        mock_email_service.send_verification_code.assert_called_once()

    @pytest.mark.asyncio
    async def test_register_duplicate_verified_email(
        self, async_client: AsyncClient, unique_email, mock_email_service
    ):
        """Test that duplicate verified email is rejected"""
        if database.db is None:
            pytest.skip("Database not connected")

        # Register and verify first user
        await async_client.post(
            "/api/auth/register",
            json={"email": unique_email, "password": "password123"},
        )

        # Manually verify the user for this test
        from app.services.users import get_user_service

        user_service = get_user_service()
        await user_service.verify_user(unique_email)

        # Try to register again
        response = await async_client.post(
            "/api/auth/register",
            json={"email": unique_email, "password": "different123"},
        )

        assert response.status_code == 409
        assert "already registered" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_register_invalid_email(self, async_client: AsyncClient):
        """Test that invalid email is rejected"""
        response = await async_client.post(
            "/api/auth/register",
            json={"email": "not-an-email", "password": "securepassword123"},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_register_short_password(
        self, async_client: AsyncClient, unique_email
    ):
        """Test that short password is rejected"""
        response = await async_client.post(
            "/api/auth/register",
            json={"email": unique_email, "password": "short"},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_register_verify_invalid_code(
        self, async_client: AsyncClient, unique_email, mock_email_service
    ):
        """Test that invalid verification code is rejected"""
        if database.db is None:
            pytest.skip("Database not connected")

        # Initiate registration
        await async_client.post(
            "/api/auth/register",
            json={"email": unique_email, "password": "password123"},
        )

        # Try to verify with wrong code
        response = await async_client.post(
            "/api/auth/register/verify",
            json={"email": unique_email, "code": "000000"},
        )

        assert response.status_code == 400
        assert "invalid" in response.json()["detail"].lower()


class TestLoginFlow:
    """Tests for 2FA login flow"""

    @pytest.mark.asyncio
    async def test_login_unverified_user(
        self, async_client: AsyncClient, unique_email, mock_email_service
    ):
        """Test that unverified user cannot login"""
        if database.db is None:
            pytest.skip("Database not connected")

        # Register but don't verify
        await async_client.post(
            "/api/auth/register",
            json={"email": unique_email, "password": "password123"},
        )

        # Try to login
        response = await async_client.post(
            "/api/auth/login",
            json={"email": unique_email, "password": "password123"},
        )

        assert response.status_code == 403
        assert "complete registration" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_login_wrong_password(
        self, async_client: AsyncClient, unique_email, mock_email_service
    ):
        """Test login with wrong password"""
        if database.db is None:
            pytest.skip("Database not connected")

        # Create verified user
        from app.services.users import get_user_service

        user_service = get_user_service()
        await user_service.create_user(
            unique_email, "correctpassword", is_verified=True
        )

        # Try login with wrong password
        response = await async_client.post(
            "/api/auth/login",
            json={"email": unique_email, "password": "wrongpassword"},
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, async_client: AsyncClient):
        """Test login with non-existent email"""
        if database.db is None:
            pytest.skip("Database not connected")

        response = await async_client.post(
            "/api/auth/login",
            json={"email": "nonexistent@example.com", "password": "anypassword"},
        )
        assert response.status_code == 401


class TestTokenRefresh:
    """Tests for token refresh"""

    @pytest.mark.asyncio
    async def test_refresh_invalid_token(self, async_client: AsyncClient):
        """Test refresh with invalid token"""
        response = await async_client.post(
            "/api/auth/refresh",
            json={"refresh_token": "invalid-token"},
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_refresh_with_access_token_fails(self, async_client: AsyncClient):
        """Test that using access token for refresh fails"""
        from app.services.jwt import get_jwt_service

        jwt_service = get_jwt_service()

        # Create an access token
        access_token = jwt_service.create_access_token("test-user-id")

        response = await async_client.post(
            "/api/auth/refresh",
            json={"refresh_token": access_token},
        )
        assert response.status_code == 401


class TestProtectedEndpoints:
    """Tests for protected endpoints"""

    @pytest.mark.asyncio
    async def test_me_without_token(self, async_client: AsyncClient):
        """Test /me endpoint without token"""
        response = await async_client.get("/api/auth/me")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_me_with_invalid_token(self, async_client: AsyncClient):
        """Test /me endpoint with invalid token"""
        response = await async_client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid-token"},
        )
        assert response.status_code == 401


class TestLogout:
    """Tests for logout endpoint"""

    @pytest.mark.asyncio
    async def test_logout_success(self, async_client: AsyncClient, unique_email):
        """Test successful logout with valid token"""
        if database.db is None:
            pytest.skip("Database not connected")

        from app.services.jwt import get_jwt_service
        from app.services.users import get_user_service

        # Create a real user in the database
        user_service = get_user_service()
        user = await user_service.create_user(
            unique_email, "password123", is_verified=True
        )

        # Create a token for that user
        jwt_service = get_jwt_service()
        access_token = jwt_service.create_access_token(user.id)

        response = await async_client.post(
            "/api/auth/logout",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Successfully logged out"

    @pytest.mark.asyncio
    async def test_logout_without_token(self, async_client: AsyncClient):
        """Test logout without token returns 401"""
        response = await async_client.post("/api/auth/logout")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_logout_with_invalid_token(self, async_client: AsyncClient):
        """Test logout with invalid token returns 401"""
        response = await async_client.post(
            "/api/auth/logout",
            headers={"Authorization": "Bearer invalid-token"},
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_logout_with_refresh_token_fails(
        self, async_client: AsyncClient, unique_email
    ):
        """Test that logout with refresh token fails (requires access token)"""
        if database.db is None:
            pytest.skip("Database not connected")

        from app.services.jwt import get_jwt_service
        from app.services.users import get_user_service

        # Create a real user in the database
        user_service = get_user_service()
        user = await user_service.create_user(
            unique_email, "password123", is_verified=True
        )

        # Try to use a refresh token instead of access token
        jwt_service = get_jwt_service()
        refresh_token = jwt_service.create_refresh_token(user.id)

        response = await async_client.post(
            "/api/auth/logout",
            headers={"Authorization": f"Bearer {refresh_token}"},
        )

        assert response.status_code == 401
