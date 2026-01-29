from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase

from app.core.config import get_settings


class Database:
    """
    MongoDB database connection manager.
    Handles connection lifecycle and provides access to collections.
    Uses PyMongo's native async support.
    """

    client: AsyncMongoClient | None = None
    db: AsyncDatabase | None = None

    async def connect(self) -> None:
        """Connect to MongoDB"""
        settings = get_settings()
        print(f"Connecting to MongoDB: {settings.mongodb_db_name}")

        self.client = AsyncMongoClient(settings.mongodb_uri)
        self.db = self.client[settings.mongodb_db_name]

        await self.client.admin.command("ping")
        print("Successfully connected to MongoDB")

    async def disconnect(self) -> None:
        """Disconnect from MongoDB"""
        if self.client:
            await self.client.close()
            print("Disconnected from MongoDB")

    def get_collection(self, name: str):
        """Get a collection by name"""
        if self.db is None:
            raise RuntimeError("Database not connected. Call connect() first")
        return self.db[name]


database = Database()


async def get_database() -> Database:
    """Get database instance"""
    return database
