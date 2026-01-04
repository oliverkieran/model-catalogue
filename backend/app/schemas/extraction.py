"""
Extraction API Schemas

Request/response models for the LLM-powered extraction endpoint.
These are separate from Model schemas because they include metadata
about the extraction process.
"""

from pydantic import BaseModel, Field
from app.models import ModelResponse


class ExtractRequest(BaseModel):
    """
    Request body for the extraction endpoint.

    Contains the raw text to extract model information from
    """

    text: str = Field(
        ...,
        min_length=10,
        description="Text to extract model information from",
        examples=[
            "GPT-5 was released by OpenAI in August 2025. It's a large multimodal model."
        ],
    )


class ExtractResponse(BaseModel):
    """
    Response from the extraction endpoint.

    Contains the created model plus metadata about the extraction process
    (useful for monitoring token usage and debugging).
    """

    model: ModelResponse = Field(description="The created model entry")

    tokens_used: int = Field(
        description="Number of tokens consumed by the LLM extraction"
    )

    llm_model: str = Field(
        description="Claude model used for extraction", examples=["claude-sonnet-4-5"]
    )


class ExtractErrorResponse(BaseModel):
    """
    Error response when extraction fails.

    Provides detailed information about what went wrong.
    """

    detail: str = Field(description="Human-readable error message")

    error_type: str = Field(
        description="Error category for client handling",
        examples=[
            "duplicate",
            "no_data_found",
            "extraction_failed",
            "validation_error",
        ],
    )
