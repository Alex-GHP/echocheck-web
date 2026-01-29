import re

from pydantic import BaseModel, Field, field_validator


def sanitize_text(text: str) -> str:
    """
    Sanitize input text by removing potentially harmful content.

    - Strips leading/trailing whitespace
    - Removes control characters (except newlines and tabs)
    - Normalizes multiple spaces to single space
    - Normalizes multiple newlines to double newline (paragraph break)
    """

    # Remove control characters except \n and \t
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]", "", text)

    # Normalize whitespace (but preserve intentional line breaks)
    text = re.sub(r"[^\S\n]+", " ", text)  # Multiple spaces/tabs to single space
    text = re.sub(r"\n{3,}", "\n\n", text)  # 3+ newlines to 2

    # Strip leading/trailing whitespace
    text = text.strip()

    return text


class ClassifyRequest(BaseModel):
    """Request body for classification endpoint"""

    text: str = Field(
        ...,
        min_length=10,
        max_length=50000,
        description="Text to classify (10-50000 characters)",
        examples=[
            "The government should increase social spending to support working families."
        ],
    )

    @field_validator("text", mode="before")
    @classmethod
    def sanitize_and_validate_text(cls, v: str) -> str:
        """Sanitize text before validation"""
        if not isinstance(v, str):
            raise ValueError("Text must be a string")

        sanitized = sanitize_text(v)

        if not sanitized or sanitized.isspace():
            raise ValueError("Text cannot be empty or whitespace only")

        return sanitized


class ProbabilityScores(BaseModel):
    """Probability scores for each political stance"""

    center: float = Field(..., ge=0.0, le=1.0)
    left: float = Field(..., ge=0.0, le=1.0)
    right: float = Field(..., ge=0.0, le=1.0)


class ClassifyResponse(BaseModel):
    """Response from classification endpoint"""

    prediction: str = Field(
        ..., description="Predicted political stance: center, left, or right"
    )
    confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Confidence score for the prediction (0-1)"
    )
    probabilities: ProbabilityScores = Field(
        ..., description="Probability scores for all three classes"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "prediction": "left",
                    "confidence": 0.873,
                    "probabilities": {"center": 0.082, "left": 0.873, "right": 0.045},
                }
            ]
        }
    }


class HealthResponse(BaseModel):
    """Health check response"""

    status: str
    model_loaded: bool
    model_name: str
