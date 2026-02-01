from datetime import UTC, datetime

from bson import ObjectId

from app.services.database import database


class FeedbackService:
    """Service for managing user feedback on classifications"""

    COLLECTION_NAME = "feedback"

    def get_collection(self):
        return database.get_collection(self.COLLECTION_NAME)

    async def create_feedback(
        self,
        text: str,
        model_prediction: str,
        model_confidence: float,
        actual_label: str,
        is_correct: bool,
        user_id: str,
    ) -> dict:
        """
        Create a new feedback entry

        Args:
            text: The classified text
            model_prediction: What the AI predicted
            model_confidence: AI's confidence score
            actual_label: The correct label (user's opinion)
            is_correct: Whether user agrees with AI
            user_id: ID of the authenticated user (required)

        Returns:
            The created feedback document with ID
        """
        collection = self.get_collection()

        feedback_doc = {
            "text": text,
            "model_prediction": model_prediction,
            "model_confidence": model_confidence,
            "actual_label": actual_label,
            "is_correct": is_correct,
            "user_id": ObjectId(user_id),
            "created_at": datetime.now(UTC),
        }

        result = await collection.insert_one(feedback_doc)
        feedback_doc["_id"] = result.inserted_id

        return feedback_doc

    async def get_feedback_stats(self) -> dict:
        """
        Get statistics about collected feedback

        Returns:
            Dictionary with total, correct, incorrect counts and accuracy rate
        """
        collection = self.get_collection()

        total = await collection.count_documents({})
        correct = await collection.count_documents({"is_correct": True})
        incorrect = total - correct

        accuracy_rate = correct / total if total > 0 else 0.0

        return {
            "total_feedback": total,
            "correct_predictions": correct,
            "incorrect_predictions": incorrect,
            "accuracy_rate": round(accuracy_rate, 4),
        }

    async def get_recent_feedback(self, limit: int = 10) -> list[dict]:
        """
        Get recent feedback entries

        Args:
            limit: Maximum number of entries to return

        Returns:
            List of recent feedback documents
        """
        collection = self.get_collection()

        cursor = collection.find().sort("created_at", -1).limit(limit)
        feedback_list = []

        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            doc["user_id"] = str(doc["user_id"])
            feedback_list.append(doc)

        return feedback_list

    async def get_incorrect_feedback(self, limit: int = 50) -> list[dict]:
        """
        Get feedback entries where the model was incorrect
        Useful for model improvement analysis

        Args:
            limit: Maximum number of entries to return

        Returns:
            List of incorrect prediction feedback documents
        """
        collection = self.get_collection()

        cursor = (
            collection.find({"is_correct": False}).sort("created_at", -1).limit(limit)
        )
        feedback_list = []

        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            doc["user_id"] = str(doc["user_id"])
            feedback_list.append(doc)

        return feedback_list

    async def get_user_feedback(self, user_id: str, limit: int = 20) -> list[dict]:
        """
        Get feedback entries from a specific user

        Args:
            user_id: The user's ID
            limit: Maximum number of entries to return

        Returns:
            List of user's feedback documents
        """
        collection = self.get_collection()

        cursor = (
            collection.find({"user_id": ObjectId(user_id)})
            .sort("created_at", -1)
            .limit(limit)
        )
        feedback_list = []

        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            doc["user_id"] = str(doc["user_id"])
            feedback_list.append(doc)

        return feedback_list


feedback_service = FeedbackService()


def get_feedback_service() -> FeedbackService:
    return feedback_service
