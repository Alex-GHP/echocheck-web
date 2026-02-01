from fastapi import APIRouter, Depends, HTTPException

from app.middleware.auth import get_current_user
from app.models.auth import UserResponse
from app.models.schemas import FeedbackRequest, FeedbackResponse, FeedbackStats
from app.services.feedback import get_feedback_service

router = APIRouter()


@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(
    request: FeedbackRequest, current_user: UserResponse = Depends(get_current_user)
) -> FeedbackResponse:
    """
    Submit feedback on a classification result

    **Authentication required** - only logged-in users can submit feedback.

    - **text**: The text that was classified
    - **model_prediction**: What the AI model predicted
    - **model_confidence**: The AI's confidence score
    - **actual_label**: The correct label (same as prediction if user agrees)
    - **is_correct**: True if user agrees with the AI, False otherwise
    """
    feedback_service = get_feedback_service()

    try:
        feedback = await feedback_service.create_feedback(
            text=request.text,
            model_prediction=request.model_prediction,
            model_confidence=request.model_confidence,
            actual_label=request.actual_label,
            is_correct=request.is_correct,
            user_id=current_user.id,
        )

        return FeedbackResponse(
            id=str(feedback["_id"]),
            message="Feedback submitted successfully",
            created_at=feedback["created_at"],
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to submit feedback: {str(e)}",
        )


@router.get("/feedback/stats", response_model=FeedbackStats)
async def get_feedback_stats() -> FeedbackStats:
    """
    Get statistics about collected feedback

    Returns total feedback count, correct/incorrect predictions, and accuracy rate.
    """
    feedback_service = get_feedback_service()

    try:
        stats = await feedback_service.get_feedback_stats()
        return FeedbackStats(**stats)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get feedback stats: {str(e)}",
        )
