import re
from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator


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


class FileType(str, Enum):
    TXT = "txt"
    PDF = "pdf"
    DOCX = "docx"


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


class FileClassifyResponse(ClassifyResponse):
    """Response from file classification endpoint"""

    filename: str = Field(..., description="Original filename that was processed")
    file_type: FileType = Field(..., description="Type of file that was processed")
    extracted_length: int = Field(
        ..., description="Number of characters extracted from the file"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "prediction": "left",
                    "confidence": 0.873,
                    "probabilities": {"center": 0.082, "left": 0.873, "right": 0.045},
                    "filename": "article.pdf",
                    "file_type": "pdf",
                    "extracted_length": 2500,
                }
            ]
        }
    }


class FeedbackRequest(BaseModel):
    """Request body for submitting feedback"""

    text: str = Field(
        ..., min_length=10, max_length=50000, description="The text that was classified"
    )
    model_prediction: Literal["left", "center", "right"] = Field(
        ...,
        description="The AI model's prediction",
    )
    model_confidence: float = Field(
        ..., ge=0.0, le=1.0, description="The AI model's confidence score"
    )
    actual_label: Literal["left", "center", "right"] = Field(
        ..., description="The correct label according to the user"
    )
    is_correct: bool = Field(
        ..., description="Whether the user agrees with the AI prediction"
    )

    @field_validator("text", mode="before")
    @classmethod
    def sanitize_feedback_text(cls, v: str) -> str:
        if not isinstance(v, str):
            raise ValueError("Text must be a string")
        return sanitize_text(v)

    @model_validator(mode="after")
    def validate_label_consistency(self) -> "FeedbackRequest":
        """Ensure actual_label is consistent with is_correct"""
        if self.is_correct is True and self.actual_label != self.model_prediction:
            raise ValueError(
                "When is_correct is true, actual_label must match model_prediction"
            )
        if self.is_correct is False and self.actual_label == self.model_prediction:
            raise ValueError(
                "When is_correct is false, actual_label must differ from model_prediction"
            )
        return self


class FeedbackResponse(BaseModel):
    """Response after submitting feedback"""

    id: str = Field(..., description="Unique feedback ID")
    message: str = Field(default="Feedback submitted successfully")
    created_at: datetime = Field(..., description="Timestamp of feedback submission")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "507f1f77bcf86cd799439011",
                    "message": "Feedback submitted successfully",
                    "created_at": "2026-02-01T12:00:00Z",
                }
            ]
        }
    }


class FeedbackStats(BaseModel):
    """Statistics about collected feedback"""

    total_feedback: int = Field(..., description="Total number of feedback entries")
    correct_predictions: int = Field(..., description="Number of correct predictions")
    incorrect_predictions: int = Field(
        ..., description="Number of incorrect predictions"
    )
    accuracy_rate: float = Field(..., description="Percentage of correct predictions")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "total_feedback": 100,
                    "correct_predictions": 85,
                    "incorrect_predictions": 15,
                    "accuracy_rate": 0.85,
                }
            ]
        }
    }


class HealthResponse(BaseModel):
    """Health check response"""

    status: str
    model_loaded: bool
    model_name: str
