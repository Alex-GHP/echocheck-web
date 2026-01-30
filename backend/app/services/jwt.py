from datetime import UTC, datetime, timedelta

import jwt
from pydantic import BaseModel

from app.core.config import get_settings


class TokenPayload(BaseModel):
    """JWT token payload structure"""

    sub: str
    exp: datetime
    iat: datetime
    type: str


class JWTService:
    """Service for JWT token operations"""

    def __init__(self):
        settings = get_settings()
        self.secret_key = settings.jwt_secret_key
        self.algorithm = settings.jwt_algorithm
        self.access_token_expire_minutes = settings.jwt_access_token_expire_minutes
        self.refresh_token_expire_days = settings.jwt_refresh_token_expire_days

    def create_access_token(self, user_id: str) -> str:
        """
        Create a new access token.

        Args:
            user_id: The user's unique identifier

        Returns:
            Encoded JWT access token
        """
        now = datetime.now(UTC)
        expire = now + timedelta(minutes=self.access_token_expire_minutes)

        payload = {"sub": user_id, "exp": expire, "iat": now, "type": "access"}

        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def create_refresh_token(self, user_id: str) -> str:
        """
        Create a new refresh token

        Args:
            user_id: The user's unique identifier

        Returns:
            Encoded JWT refresh token
        """
        now = datetime.now(UTC)
        expire = now + timedelta(days=self.refresh_token_expire_days)

        payload = {
            "sub": user_id,
            "exp": expire,
            "iat": now,
            "type": "refresh",
        }

        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def create_token_pair(self, user_id: str) -> dict:
        """
        Create both access and refresh tokens

        Args:
            user_id: The user's unique identifier

        Returns:
            Dictionary with access_token, refresh_token, token_type, and expires_in
        """
        return {
            "access_token": self.create_access_token(user_id),
            "refresh_token": self.create_refresh_token(user_id),
            "token_type": "bearer",
            "expires_in": self.access_token_expire_minutes * 60,
        }

    def verify_token(
        self, token: str, expected_type: str = "access"
    ) -> TokenPayload | None:
        """
        Verify and decode a JWT token

        Args:
            token: The JWT token to verify
            expected_type: Expected token type ("access" or "refresh")

        Returns:
            TokenPayload if valid, None if invalid
        """
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
            )

            if payload.get("type") != expected_type:
                return None

            return TokenPayload(**payload)

        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    def get_user_id_from_token(
        self, token: str, expected_type: str = "access"
    ) -> str | None:
        """
        Extract user ID from a valid token

        Args:
            token: The JWT token
            expected_type: Expected token type ("access" or "refresh")

        Returns:
            User ID if token is valid, None otherwise
        """
        payload = self.verify_token(token, expected_type)
        return payload.sub if payload else None


jwt_service = JWTService()


def get_jwt_service() -> JWTService:
    return jwt_service
