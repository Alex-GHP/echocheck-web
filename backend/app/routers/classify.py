from fastapi import APIRouter, HTTPException

from app.models.schemas import ClassifyRequest, ClassifyResponse
from app.services.classifier import get_classifier

router = APIRouter()


@router.post("/classify", response_model=ClassifyResponse)
async def classify_text(request: ClassifyRequest) -> ClassifyResponse:
    """
    Classify the political stance of the provided text.

    - **text**: The article or statement to classify (10-50000 characters)

    Returns the predicted political stance (left, center, right),
    confidence score, and probability distribution across all classes.
    """
    try:
        classifier = get_classifier()
        result = classifier.predict(request.text)
        return ClassifyResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Classification failed: {str(e)}")
