"""
Extraction API Router

Provides endpoints for LLM-powered data extraction and insertion.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db import get_db
from app.services.llm_service import LLMService
from app.schemas.extraction import ExtractRequest, ExtractResponse
from app.api.v1.extraction_helpers import (
    convert_extracted_to_create,
    validate_extracted_data,
)
from app.api.v1.models import create_model

import logging

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/api/v1",
    tags=["extraction"],
    responses={
        400: {"description": "Invalid request or no data found"},
        409: {"description": "Model already exists"},
        500: {"description": "Extraction or database error"},
    },
)


@router.post("/extract", response_model=ExtractResponse, status_code=201)
async def extract_and_create_model(
    request: ExtractRequest,
    llm_service: LLMService = Depends(LLMService),
    session: AsyncSession = Depends(get_db),
) -> ExtractResponse:
    """
    Extract AI model information from text and create database entry.

    This endpoint uses a LLM (Claude) to automatically parse unstructured text
    (research papers, blog posts, announcements) and extract model information.

    The extraction process:
    1. LLM reads the text and identifies model information
    2. Extracted data is validated against schemas
    3. Converted to ModelCreate schema
    4. Model is created using the existing create_model endpoint logic
    5. Response includes the model and extraction metadata

    Args:
        request: Text containing model information
        llm_service: Injected LLMService instance
        session: Database session

    Returns:
        ExtractResponse with created model and token usage

    Raises:
        HTTPException(400): Empty text or no model information found
        HTTPException(409): Model with same name already exists
        HTTPException(500): LLM API error or database failure

    Example:
        POST /api/v1/extract
        {
            "text": "GPT-4 was released by OpenAI in March 2023..."
        }

        Response (201 Created):
        {
            "model": {
                "id": 1,
                "name": "gpt-4",
                "organization": "OpenAI",
                "release_date": "2023-03-01",
                ...
            },
            "tokens_used": 650,
            "llm_model": "claude-sonnet-4-5"
        }
    """

    logger.info(
        f"Extraction request received (text length: {len(request.text)} characters)"
    )

    # Step 1: Extract data using LLM
    try:
        extraction_result = await llm_service.extract_model_data(
            text=request.text, use_cache=True  # Enable caching to reduce costs
        )
    except ValueError as e:
        logger.error(f"Extraction validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Catch all other errors (API failures, network issues, etc.)
        logger.error(f"LLM extraction failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to extract model information from text: {str(e)}",
        )

    logger.info(
        f"Extraction complete: {extraction_result.tokens_used} tokens, "
        f"model: {extraction_result.model_used}"
    )

    # Step 2: Validate extraction produced data
    validate_extracted_data(extraction_result.data)

    # Step 3: Convert to ModelCreate schema
    model_create = convert_extracted_to_create(extraction_result.data)
    logger.info(f"Extracted model: {model_create.name} by {model_create.organization}")

    # Step 4: Reuse existing create_model endpoint logic
    # This handles duplicate checking, validation, and database insertion
    created_model = await create_model(model_data=model_create, session=session)

    logger.info(
        f"Model created successfully: {created_model.name} (id={created_model.id})"
    )

    # Step 5: Build response with extraction metadata
    return ExtractResponse(
        model=created_model,
        tokens_used=extraction_result.tokens_used,
        llm_model=extraction_result.model_used,
    )
