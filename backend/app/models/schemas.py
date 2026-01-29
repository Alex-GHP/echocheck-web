from pydantic import BaseModel, Field


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
