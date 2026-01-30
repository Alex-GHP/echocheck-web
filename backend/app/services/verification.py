import secrets
from datetime import UTC, datetime, timedelta

from app.core.config import get_settings
from app.models.auth import VerificationType
from app.services.database import database
from app.services.email import get_email_service


class VerificationService:
    COLLECTION_NAME = "verification_codes"

    def __init__(self):
        settings = get_settings()
        self.expire_minutes = settings.verification_code_expire_minutes
        self.code_length = settings.verification_code_length

    def _get_collection(self):
        return database.get_collection(self.COLLECTION_NAME)

    def _generate_code(self) -> str:
        max_value = 10**self.code_length - 1
        code = secrets.randbelow(max_value + 1)
        return str(code).zfill(self.code_length)

    async def create_and_send_code(
        self, email: str, verification_type: VerificationType
    ) -> bool:
        """
        Create a verification code and send it via email

        Args:
            email: User's email address
            verification_type: Type of verification (registration or login)

        Returns:
            True if code was created and email sent, False otherwise
        """
        collection = self._get_collection()
        email_service = get_email_service()

        await collection.update_many(
            {"email": email.lower(), "type": verification_type.value, "used": False},
            {"$set": {"used": True}},
        )

        code = self._generate_code()
        now = datetime.now(UTC)
        expires_at = now + timedelta(minutes=self.expire_minutes)

        code_doc = {
            "email": email.lower(),
            "code": code,
            "type": verification_type.value,
            "expires_at": expires_at,
            "created_at": now,
            "used": False,
        }

        await collection.insert_one(code_doc)

        success = email_service.send_verification_code(
            to_email=email,
            code=code,
            verification_type=verification_type.value,
            expires_minutes=self.expire_minutes,
        )

        return success

    async def verify_code(
        self,
        email: str,
        code: str,
        verification_type: VerificationType,
    ) -> bool:
        """
        Verify a code and mark it as used

        Args:
            email: User's email address
            code: The verification code to check
            verification_type: Type of verification

        Returns:
            True if code is valid, False otherwise
        """
        collection = self._get_collection()
        now = datetime.now(UTC)

        code_doc = await collection.find_one(
            {
                "email": email.lower(),
                "code": code,
                "type": verification_type.value,
                "used": False,
                "expires_at": {"$gt": now},
            }
        )

        if not code_doc:
            return False

        await collection.update_one(
            {"_id": code_doc["_id"]},
            {"$set": {"used": True}},
        )

        return True

    async def has_pending_code(
        self,
        email: str,
        verification_type: VerificationType,
    ) -> bool:
        """
        Check if there's a valid pending code for the email

        Args:
            email: User's email address
            verification_type: Type of verification

        Returns:
            True if there's a valid pending code
        """
        collection = self._get_collection()
        now = datetime.now(UTC)

        code_doc = await collection.find_one(
            {
                "email": email.lower(),
                "type": verification_type.value,
                "used": False,
                "expires_at": {"$gt": now},
            }
        )

        return code_doc is not None

    async def setup_indexes(self):
        """
        Create necessary indexes for the collection
        Call this on app startup.
        """
        collection = self._get_collection()

        await collection.create_index(
            "expires_at",
            expireAfterSeconds=3600,
        )

        await collection.create_index(
            [
                ("email", 1),
                ("type", 1),
                ("used", 1),
                ("expires_at", 1),
            ]
        )


verification_service = VerificationService()


def get_verification_service() -> VerificationService:
    return verification_service
