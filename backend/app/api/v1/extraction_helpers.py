"""
Extraction Endpoint Helper Functions

Business logic for the extraction endpoint, separated for testability.
"""

from datetime import date
from app.services.llm_service import ExtractedModel
from app.models import ModelCreate


def validate_extracted_data(extracted: ExtractedModel | None) -> None:
    """
    Validate that extraction produced usable data.

    Raises HTTPException with appropriate status code if data is invalid.

    Args:
        extracted: Extracted model data (or None if extraction failed)

    Raises:
        HTTPException(400): If no data was extracted
        HTTPException(422): If required fields are missing
    """
    from fastapi import HTTPException

    if extracted is None:
        raise HTTPException(
            status_code=400,
            detail="No model information could be extracted from the provided text. "
            "Please ensure the text contains information about an AI model.",
        )


def convert_extracted_to_create(extracted: ExtractedModel) -> ModelCreate:
    """
    Convert LLM-extracted data to ModelCreate schema.

    Maps field names and ensures data types match the database schema.

    Args:
        extracted: Data extracted by LLMService

    Returns:
        ModelCreate schema ready for database insertion
    """
    return ModelCreate(
        name=extracted.model_name,
        display_name=extracted.model_name,  # TODO: Should be more user-friendly than the technical name
        organization=extracted.organization,
        release_date=extracted.release_date,
        description=extracted.description,
        license=extracted.license,
    )
