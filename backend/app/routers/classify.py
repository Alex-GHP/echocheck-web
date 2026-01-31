from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.middleware.auth import get_current_user
from app.models.auth import UserResponse
from app.models.schemas import ClassifyRequest, ClassifyResponse, FileClassifyResponse
from app.services.classifier import get_classifier
from app.services.file_extractor import get_file_extractor

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


@router.post("/classify/file", response_model=FileClassifyResponse)
async def classify_file(
    file: UploadFile = File(..., description="Document file to classify"),
    current_user: UserResponse = Depends(get_current_user),
) -> FileClassifyResponse:
    """
    Classify the political stance of text extracted from an uploaded file.

    **Authentication required** - only logged-in users can upload files.

    Supported file types:
    - `.txt` - Plain text files
    - `.pdf` - PDF documents
    - `.docx` - Microsoft Word documents

    Maximum file size: 10MB

    Returns the predicted political stance along with file metadata.
    """
    _ = current_user

    file_extractor = get_file_extractor()

    text, file_type, safe_filename = await file_extractor.extract_text(file)

    try:
        classifier = get_classifier()
        result = classifier.predict(text)

        return FileClassifyResponse(
            prediction=result["prediction"],
            confidence=result["confidence"],
            probabilities=result["probabilities"],
            filename=safe_filename,
            file_type=file_type,
            extracted_length=len(text),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Classification failed: {str(e)}")
