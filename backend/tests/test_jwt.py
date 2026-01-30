import pytest

from app.services.jwt import JWTService


@pytest.fixture
def jwt_service():
    """Create a JWT service instance for testing"""
    return JWTService()


class TestJWTService:
    """Tests for JWT service"""

    def test_create_access_token(self, jwt_service):
        """Test creating an access token"""
        user_id = "test-user-123"
        token = jwt_service.create_access_token(user_id)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_refresh_token(self, jwt_service):
        """Test creating a refresh token"""
        user_id = "test-user-123"
        token = jwt_service.create_refresh_token(user_id)

        assert token is not None
        assert isinstance(token, str)

    def test_create_token_pair(self, jwt_service):
        """Test creating a token pair"""
        user_id = "test-user-123"
        tokens = jwt_service.create_token_pair(user_id)

        assert "access_token" in tokens
        assert "refresh_token" in tokens
        assert "token_type" in tokens
        assert tokens["token_type"] == "bearer"

    def test_verify_valid_access_token(self, jwt_service):
        """Test verifying a valid access token"""
        user_id = "test-user-123"
        token = jwt_service.create_access_token(user_id)
        payload = jwt_service.verify_token(token, expected_type="access")

        assert payload is not None
        assert payload.sub == user_id
        assert payload.type == "access"

    def test_verify_valid_refresh_token(self, jwt_service):
        """Test verifying a valid refresh token"""
        user_id = "test-user-123"
        token = jwt_service.create_refresh_token(user_id)
        payload = jwt_service.verify_token(token, expected_type="refresh")

        assert payload is not None
        assert payload.sub == user_id
        assert payload.type == "refresh"

    def test_verify_wrong_token_type(self, jwt_service):
        """Test that verifying with wrong type fails"""
        user_id = "test-user-123"
        access_token = jwt_service.create_access_token(user_id)
        payload = jwt_service.verify_token(access_token, expected_type="refresh")
        assert payload is None

    def test_verify_invalid_token(self, jwt_service):
        """Test that invalid token fails verification"""
        payload = jwt_service.verify_token("invalid-token", expected_type="access")
        assert payload is None

    def test_get_user_id_from_token(self, jwt_service):
        """Test extracting user ID from token"""
        user_id = "test-user-123"
        token = jwt_service.create_access_token(user_id)
        extracted_id = jwt_service.get_user_id_from_token(token)
        assert extracted_id == user_id

    def test_access_and_refresh_tokens_are_different(self, jwt_service):
        """Test that access and refresh tokens are different"""
        user_id = "test-user-123"
        access = jwt_service.create_access_token(user_id)
        refresh = jwt_service.create_refresh_token(user_id)
        assert access != refresh
