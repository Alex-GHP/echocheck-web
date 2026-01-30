import resend

from app.core.config import get_settings


class EmailService:
    """Email service using Resend API"""

    def __init__(self):
        settings = get_settings()
        resend.api_key = settings.resend_api_key
        self.from_email = settings.resend_from_email

    def send_verification_code(
        self,
        to_email: str,
        code: str,
        verification_type: str,
        expires_minutes: int,
    ) -> bool:
        """
        Send a verification code email

        Args:
            to_email: Recipient email address
            code: The 6-digit verification code
            verification_type: "registration" or "login"
            expires_minutes: Minutes until code expires

        Returns:
            True if email sent successfully, False otherwise
        """
        if verification_type == "registration":
            subject = "EchoCheck - Verify Your Email"
            action_text = "complete your registration"
        else:
            subject = "EchoCheck - Login Verification Code"
            action_text = "log in to your account"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="text-align: center; margin-bottom: 30px;">
                <h1 style="color: #2563eb; margin: 0;">EchoCheck</h1>
                <p style="color: #6b7280; margin-top: 5px;">Political Stance Classification</p>
            </div>

            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 12px; padding: 30px; text-align: center; margin-bottom: 30px;">
                <p style="color: #fff; margin: 0 0 15px 0; font-size: 16px;">
                    Your verification code to {action_text}:
                </p>
                <div style="background: #fff; border-radius: 8px; padding: 20px; display: inline-block;">
                    <span style="font-size: 32px; font-weight: bold; letter-spacing: 8px; color: #1f2937;">
                        {code}
                    </span>
                </div>
            </div>

            <div style="background: #f3f4f6; border-radius: 8px; padding: 20px; margin-bottom: 20px;">
                <p style="margin: 0; color: #4b5563; font-size: 14px;">
                    ⏱️ This code expires in <strong>{expires_minutes} minutes</strong>.
                </p>
                <p style="margin: 10px 0 0 0; color: #4b5563; font-size: 14px;">
                    🔒 If you didn't request this code, you can safely ignore this email.
                </p>
            </div>

            <div style="text-align: center; color: #9ca3af; font-size: 12px; margin-top: 30px;">
                <p style="margin: 0;">
                    This email was sent by EchoCheck. Please do not reply to this email.
                </p>
            </div>
        </body>
        </html>
        """

        text_content = f"""
EchoCheck - Verification Code

Your verification code to {action_text}: {code}

This code expires in {expires_minutes} minutes.

If you didn't request this code, you can safely ignore this email.
        """

        try:
            params: resend.Emails.SendParams = {
                "from": self.from_email,
                "to": [to_email],
                "subject": subject,
                "html": html_content,
                "text": text_content,
            }

            result = resend.Emails.send(params)

            if result is None:
                return False
            if isinstance(result, dict):
                return "id" in result
            return hasattr(result, "id")

        except Exception as e:
            print(f"Failed to send email: {e}")
            return False

    def send_welcome_email(self, to_email: str) -> bool:
        """
        Send a welcome email after successful registration

        Args:
            to_email: Recipient email address

        Returns:
            True if email sent successfully, False otherwise
        """
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="text-align: center; margin-bottom: 30px;">
                <h1 style="color: #2563eb; margin: 0;">Welcome to EchoCheck! 🎉</h1>
            </div>

            <div style="background: #f0fdf4; border: 1px solid #86efac; border-radius: 12px; padding: 25px; margin-bottom: 25px;">
                <p style="margin: 0; color: #166534; font-size: 16px;">
                    Your account has been successfully created and verified!
                </p>
            </div>

            <p style="color: #4b5563;">
                You can now use EchoCheck to:
            </p>
            <ul style="color: #4b5563;">
                <li>Classify political stance of articles and statements</li>
                <li>Upload documents for batch analysis</li>
                <li>Provide feedback to improve our model</li>
            </ul>

            <div style="text-align: center; color: #9ca3af; font-size: 12px; margin-top: 30px;">
                <p style="margin: 0;">
                    Thank you for using EchoCheck!
                </p>
            </div>
        </body>
        </html>
        """

        try:
            params: resend.Emails.SendParams = {
                "from": self.from_email,
                "to": [to_email],
                "subject": "Welcome to EchoCheck! 🎉",
                "html": html_content,
            }

            result = resend.Emails.send(params)

            if result is None:
                return False
            if isinstance(result, dict):
                return "id" in result
            return hasattr(result, "id")

        except Exception as e:
            print(f"Failed to send welcome email: {e}")
            return False


email_service = EmailService()


def get_email_service() -> EmailService:
    return email_service
