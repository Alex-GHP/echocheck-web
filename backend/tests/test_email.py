from unittest.mock import MagicMock, patch

import pytest

from app.services.email import EmailService


class TestEmailService:
    """Tests for email service"""

    @pytest.fixture
    def email_service(self):
        """Create email service instance"""
        return EmailService()

    def test_send_verification_code_registration(self, email_service):
        """Test sending registration verification code"""
        with patch("app.services.email.resend.Emails.send") as mock_send:
            mock_result = MagicMock()
            mock_result.id = "email-id-123"
            mock_send.return_value = mock_result

            result = email_service.send_verification_code(
                to_email="test@example.com",
                code="123456",
                verification_type="registration",
                expires_minutes=10,
            )

            assert result is True
            mock_send.assert_called_once()

    def test_send_verification_code_login(self, email_service):
        """Test sending login verification code"""
        with patch("app.services.email.resend.Emails.send") as mock_send:
            mock_result = MagicMock()
            mock_result.id = "email-id-123"
            mock_send.return_value = mock_result

            result = email_service.send_verification_code(
                to_email="test@example.com",
                code="654321",
                verification_type="login",
                expires_minutes=10,
            )

            assert result is True

    def test_send_verification_code_failure(self, email_service):
        """Test handling email send failure"""
        with patch("app.services.email.resend.Emails.send") as mock_send:
            mock_send.side_effect = Exception("API error")

            result = email_service.send_verification_code(
                to_email="test@example.com",
                code="123456",
                verification_type="registration",
                expires_minutes=10,
            )

            assert result is False

    def test_send_welcome_email(self, email_service):
        """Test sending welcome email"""
        with patch("app.services.email.resend.Emails.send") as mock_send:
            mock_result = MagicMock()
            mock_result.id = "email-id-123"
            mock_send.return_value = mock_result

            result = email_service.send_welcome_email("test@example.com")

            assert result is True
