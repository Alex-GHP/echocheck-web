import io

import pytest
from httpx import AsyncClient

from app.services.database import database
from app.services.jwt import get_jwt_service
from app.services.users import get_user_service


class TestFileUploadEndpoint:
    """Tests for POST /api/classify/file"""

    @pytest.mark.asyncio
    async def test_upload_without_auth(self, async_client: AsyncClient):
        """Should reject unauthenticated requests"""
        content = b"This is political content about government policy and taxation."
        files = {"file": ("test.txt", io.BytesIO(content), "text/plain")}

        response = await async_client.post("/api/classify/file", files=files)

        assert response.status_code == 401  # HTTPBearer returns 401 without token

    @pytest.mark.asyncio
    async def test_upload_with_invalid_token(self, async_client: AsyncClient):
        """Should reject invalid tokens"""
        content = b"This is political content about government policy and taxation."
        files = {"file": ("test.txt", io.BytesIO(content), "text/plain")}

        response = await async_client.post(
            "/api/classify/file",
            files=files,
            headers={"Authorization": "Bearer invalid-token"},
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_upload_txt_file_success(self, async_client: AsyncClient):
        """Should classify text from uploaded txt file"""
        if database.db is None:
            pytest.skip("MongoDB not available")

        # Create a test user and get token
        user_service = get_user_service()
        jwt_service = get_jwt_service()

        # Clean up any existing test user
        try:
            existing = await user_service.get_user_by_email("filetest@example.com")
            if existing:
                collection = database.get_collection("users")
                await collection.delete_one({"email": "filetest@example.com"})
        except Exception:
            pass

        # Create user
        user = await user_service.create_user(
            email="filetest@example.com",
            password="testpassword123",
        )
        await user_service.verify_user(str(user.id))

        # Generate token
        access_token = jwt_service.create_access_token(str(user.id))

        # Upload file
        content = b"""
        This is a comprehensive article about government policy.
        The government should increase social spending to support working families.
        Progressive taxation can help reduce income inequality.
        Universal healthcare is essential for all citizens.
        """
        files = {"file": ("article.txt", io.BytesIO(content), "text/plain")}

        response = await async_client.post(
            "/api/classify/file",
            files=files,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "prediction" in data
        assert data["prediction"] in ["left", "center", "right"]
        assert "confidence" in data
        assert "probabilities" in data
        assert data["filename"] == "article.txt"
        assert data["file_type"] == "txt"
        assert data["extracted_length"] > 0

        # Cleanup
        collection = database.get_collection("users")
        await collection.delete_one({"email": "filetest@example.com"})

    @pytest.mark.asyncio
    async def test_upload_unsupported_file_type(self, async_client: AsyncClient):
        """Should reject unsupported file types"""
        if database.db is None:
            pytest.skip("MongoDB not available")

        # Create a test user and get token
        user_service = get_user_service()
        jwt_service = get_jwt_service()

        try:
            existing = await user_service.get_user_by_email("filetest2@example.com")
            if existing:
                collection = database.get_collection("users")
                await collection.delete_one({"email": "filetest2@example.com"})
        except Exception:
            pass

        user = await user_service.create_user(
            email="filetest2@example.com",
            password="testpassword123",
        )
        await user_service.verify_user(str(user.id))
        access_token = jwt_service.create_access_token(str(user.id))

        # Upload unsupported file
        files = {
            "file": (
                "malware.exe",
                io.BytesIO(b"binary content"),
                "application/octet-stream",
            )
        }

        response = await async_client.post(
            "/api/classify/file",
            files=files,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 400
        assert "Unsupported file type" in response.json()["detail"]

        # Cleanup
        collection = database.get_collection("users")
        await collection.delete_one({"email": "filetest2@example.com"})

    @pytest.mark.asyncio
    async def test_upload_empty_file(self, async_client: AsyncClient):
        """Should reject empty files"""
        if database.db is None:
            pytest.skip("MongoDB not available")

        user_service = get_user_service()
        jwt_service = get_jwt_service()

        try:
            existing = await user_service.get_user_by_email("filetest3@example.com")
            if existing:
                collection = database.get_collection("users")
                await collection.delete_one({"email": "filetest3@example.com"})
        except Exception:
            pass

        user = await user_service.create_user(
            email="filetest3@example.com",
            password="testpassword123",
        )
        await user_service.verify_user(str(user.id))
        access_token = jwt_service.create_access_token(str(user.id))

        # Upload empty file
        files = {"file": ("empty.txt", io.BytesIO(b""), "text/plain")}

        response = await async_client.post(
            "/api/classify/file",
            files=files,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 400
        assert "empty" in response.json()["detail"].lower()

        # Cleanup
        collection = database.get_collection("users")
        await collection.delete_one({"email": "filetest3@example.com"})

    @pytest.mark.asyncio
    async def test_upload_file_text_too_short(self, async_client: AsyncClient):
        """Should reject files with text that's too short after extraction"""
        if database.db is None:
            pytest.skip("MongoDB not available")

        user_service = get_user_service()
        jwt_service = get_jwt_service()

        try:
            existing = await user_service.get_user_by_email("filetest4@example.com")
            if existing:
                collection = database.get_collection("users")
                await collection.delete_one({"email": "filetest4@example.com"})
        except Exception:
            pass

        user = await user_service.create_user(
            email="filetest4@example.com",
            password="testpassword123",
        )
        await user_service.verify_user(str(user.id))
        access_token = jwt_service.create_access_token(str(user.id))

        # Upload file with too short content
        files = {"file": ("short.txt", io.BytesIO(b"Too short"), "text/plain")}

        response = await async_client.post(
            "/api/classify/file",
            files=files,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 400
        assert "too short" in response.json()["detail"].lower()

        # Cleanup
        collection = database.get_collection("users")
        await collection.delete_one({"email": "filetest4@example.com"})


class TestFileUploadValidation:
    """Tests for file validation edge cases"""

    @pytest.mark.asyncio
    async def test_no_file_provided(self, async_client: AsyncClient):
        """Should fail when no file is provided"""
        if database.db is None:
            pytest.skip("MongoDB not available")

        user_service = get_user_service()
        jwt_service = get_jwt_service()

        try:
            existing = await user_service.get_user_by_email("filetest5@example.com")
            if existing:
                collection = database.get_collection("users")
                await collection.delete_one({"email": "filetest5@example.com"})
        except Exception:
            pass

        user = await user_service.create_user(
            email="filetest5@example.com",
            password="testpassword123",
        )
        await user_service.verify_user(str(user.id))
        access_token = jwt_service.create_access_token(str(user.id))

        response = await async_client.post(
            "/api/classify/file",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 422  # Validation error

        # Cleanup
        collection = database.get_collection("users")
        await collection.delete_one({"email": "filetest5@example.com"})
