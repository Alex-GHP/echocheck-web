from datetime import UTC, datetime

from bson import ObjectId

from app.models.auth import UserInDB, UserResponse
from app.services.database import database
from app.services.password import hash_password, verify_password


class UserService:
    COLLECTION_NAME = "users"

    def _get_collection(self):
        return database.get_collection(self.COLLECTION_NAME)

    async def create_user(
        self, email: str, password: str, is_verified: bool = False
    ) -> UserResponse:
        """
        Create a new user (initially unverified)

        Args:
            email: User's email address
            password: Plain text password (will be hashed)
            is_verified: Whether the user is already verified

        Returns:
            UserResponse with the created user's info

        Raises:
            ValueError: If email already exists
        """
        collection = self._get_collection()

        existing = await collection.find_one({"email": email.lower()})
        if existing:
            raise ValueError("Email already registered")

        now = datetime.now(UTC)
        user_doc = {
            "email": email.lower(),
            "password_hash": hash_password(password),
            "is_verified": is_verified,
            "created_at": now,
        }

        result = await collection.insert_one(user_doc)

        return UserResponse(
            id=str(result.inserted_id),
            email=email.lower(),
            is_verified=is_verified,
            created_at=now,
        )

    async def get_user_by_email(self, email: str) -> UserInDB | None:
        """
        Get a user by email address

        Args:
            email: User's email address

        Returns:
            UserInDB if found, None otherwise
        """
        collection = self._get_collection()
        user_doc = await collection.find_one({"email": email.lower()})

        if not user_doc:
            return None

        return UserInDB(
            id=str(user_doc["_id"]),
            email=user_doc["email"],
            password_hash=user_doc["password_hash"],
            is_verified=user_doc.get("is_verified", False),
            created_at=user_doc["created_at"],
        )

    async def get_user_by_id(self, user_id: str) -> UserResponse | None:
        """
        Get a user by ID

        Args:
            user_id: User's unique identifier

        Returns:
            UserResponse if found, None otherwise
        """
        collection = self._get_collection()

        try:
            user_doc = await collection.find_one({"_id": ObjectId(user_id)})
        except Exception:
            return None

        if not user_doc:
            return None

        return UserResponse(
            id=str(user_doc["_id"]),
            email=user_doc["email"],
            is_verified=user_doc.get("is_verified", False),
            created_at=user_doc["created_at"],
        )

    async def verify_user(self, email: str) -> bool:
        """
        Mark a user as verified

        Args:
            email: User's email address

        Returns:
            True if user was verified, False if not found
        """
        collection = self._get_collection()

        result = await collection.update_one(
            {"email": email.lower()},
            {"$set": {"is_verified": True}},
        )

        return result.modified_count > 0

    async def authenticate_user(self, email: str, password: str) -> UserInDB | None:
        """
        Authenticate a user with email and password

        Args:
            email: User's email address
            password: Plain text password

        Returns:
            UserInDB if authentication successful, None otherwise
        """
        user = await self.get_user_by_email(email)

        if not user:
            return None

        if not verify_password(password, user.password_hash):
            return None

        return user

    async def email_exists(self, email: str) -> bool:
        """
        Check if an email is already registered

        Args:
            email: Email to check

        Returns:
            True if email exists, False otherwise
        """
        collection = self._get_collection()
        user_doc = await collection.find_one({"email": email.lower()})
        return user_doc is not None

    async def delete_unverified_user(self, email: str) -> bool:
        """
        Delete an unverified user (for re-registration)

        Args:
            email: User's email address

        Returns:
            True if deleted, False otherwise
        """
        collection = self._get_collection()

        result = await collection.delete_one(
            {
                "email": email.lower(),
                "is_verified": False,
            }
        )

        return result.deleted_count > 0

    async def setup_indexes(self):
        """
        Create necessary indexes for the collection
        Call this on app startup.
        """
        collection = self._get_collection()

        await collection.create_index("email", unique=True)


user_service = UserService()


def get_user_service() -> UserService:
    return user_service
