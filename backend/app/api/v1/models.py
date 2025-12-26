"""
Models API Router

Provides REST endpoints for AI model management:
- List models with pagination
- Get individual model details
- Search models (coming in Module 2.2)
- Create/Update/Delete models (coming in Module 2.2)
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Sequence

from app.db import get_db
from app.db.repositories import ModelRepository
from app.models.models import ModelResponse

# Create router with prefix and tags
router = APIRouter(
    prefix="/api/v1/models",
    tags=["models"],
    responses={
        404: {"description": "Model not found"},
    },
)


@router.get("/", response_model=list[ModelResponse])
async def list_models(
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        default=10, ge=1, le=1000, description="Maximum number of records to return"
    ),
    session: AsyncSession = Depends(get_db),
) -> Sequence[ModelResponse]:
    """
    List all AI models with pagination.

    - **skip**: Number of records to skip (for pagination)
    - **limit**: Maximum number of records to return (max 100)

    Returns a list of AI models with their basic information.
    """
    repo = ModelRepository(session)
    models = await repo.get_all(skip=skip, limit=limit)
    return models


@router.get("/{model_id}", response_model=ModelResponse)
async def get_model(
    model_id: int,
    session: AsyncSession = Depends(get_db),
) -> ModelResponse:
    """
    Get a specific AI model by ID.

    - **model_id**: The unique identifier of the model

    Returns detailed information about the model including metadata.

    Raises:
        HTTPException 404: If model with given ID doesn't exist
    """
    repo = ModelRepository(session)
    model = await repo.get_by_id(model_id)

    if not model:
        raise HTTPException(
            status_code=404, detail=f"Model with id {model_id} not found"
        )

    return model


@router.get("/name/{model_name}", response_model=ModelResponse)
async def get_model_by_name(
    model_name: str,
    session: AsyncSession = Depends(get_db),
) -> ModelResponse:
    """
    Get a specific AI model by its unique name.

    - **model_name**: The unique name of the model (e.g., "gpt-4", "claude-3-opus")

    Returns detailed information about the model.

    Raises:
        HTTPException 404: If model with given name doesn't exist
    """
    repo = ModelRepository(session)
    model = await repo.get_by_name(model_name)

    if not model:
        raise HTTPException(
            status_code=404, detail=f"Model with name '{model_name}' not found"
        )

    return model
