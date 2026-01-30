from datetime import datetime
from enum import Enum

from pydantic import BaseModel, EmailStr, Field


class VerificationType(str, Enum):
    """Types of verification codes"""

    REGISTRATION = "registration"
    LOGIN = "login"


class RegisterInitRequest(BaseModel):
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Password (8-128 characters)",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "user@example.com",
                    "password": "securepassword123",
                }
            ]
        }
    }


class RegisterVerifyRequest(BaseModel):
    email: EmailStr = Field(..., description="User's email address")
    code: str = Field(
        ...,
        min_length=6,
        max_length=6,
        description="6-digit verification code",
    )


class LoginInitRequest(BaseModel):
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")


class LoginVerifyRequest(BaseModel):
    email: EmailStr = Field(..., description="User's email address")
    code: str = Field(
        ...,
        min_length=6,
        max_length=6,
        description="6-digit verification code",
    )


class TokenRefreshRequest(BaseModel):
    """Request body for token refresh"""

    refresh_token: str = Field(..., description="Valid refresh token")


class ResendCodeRequest(BaseModel):
    """Request to resend verification code"""

    email: EmailStr = Field(..., description="User's email address")
    type: VerificationType = Field(..., description="Type of verification")


class UserResponse(BaseModel):
    """User information returned in responses"""

    id: str = Field(..., description="User's unique identifier")
    email: EmailStr = Field(..., description="User's email address")
    is_verified: bool = Field(..., description="Whether email is verified")
    created_at: datetime = Field(..., description="Account creation timestamp")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "507f1f77bcf86cd799439011",
                    "email": "user@example.com",
                    "is_verified": True,
                    "created_at": "2026-01-29T12:00:00Z",
                }
            ]
        }
    }


class TokenResponse(BaseModel):
    """JWT token pair response"""

    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Access token expiry in seconds")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "token_type": "bearer",
                    "expires_in": 1800,
                }
            ]
        }
    }


class AuthResponse(BaseModel):
    """Combined auth response with user info and tokens"""

    user: UserResponse
    tokens: TokenResponse


class VerificationSentResponse(BaseModel):
    """Response when verification code is sent"""

    message: str = Field(..., description="Success message")
    email: EmailStr = Field(..., description="Email address code was sent to")
    expires_in_minutes: int = Field(..., description="Code expiry time in minutes")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "message": "Verification code sent",
                    "email": "user@example.com",
                    "expires_in_minutes": 10,
                }
            ]
        }
    }


class MessageResponse(BaseModel):
    """Simple message response"""

    message: str


class UserInDB(BaseModel):
    """User model as stored in database"""

    id: str
    email: str
    password_hash: str
    is_verified: bool
    created_at: datetime


class VerificationCodeInDB(BaseModel):
    """Verification code as stored in database"""

    id: str
    email: str
    code: str
    type: VerificationType
    expires_at: datetime
    created_at: datetime
    used: bool
