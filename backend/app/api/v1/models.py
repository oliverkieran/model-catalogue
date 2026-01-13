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
from app.db.repositories import (
    ModelRepository,
    BenchmarkResultRepository,
    OpinionRepository,
    UseCaseRepository,
)
from app.models.models import (
    Model,
    ModelCreate,
    ModelResponse,
    ModelUpdate,
    BenchmarkResultResponse,
    OpinionResponse,
    UseCaseResponse,
)

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


@router.get("/search/", response_model=list[ModelResponse])
async def search_models(
    q: str = Query(
        ..., min_length=2, description="Search query (minimum 2 characters)"
    ),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, le=100),
    session: AsyncSession = Depends(get_db),
) -> Sequence[ModelResponse]:
    """
    Search for models by name or organization.

    The search is case-insensitive and matches partial strings.
    Searches across name and organization fields.

    Args:
        q: Search query (minimum 2 characters)
        skip: Pagination offset
        limit: Maximum results

    Returns:
        List of models matching the search query

    Examples:
        /api/v1/models/search/?q=gpt       # Find all GPT models
        /api/v1/models/search/?q=openai    # Find all OpenAI models
        /api/v1/models/search/?q=coding    # Find models mentioning coding
    """
    repo = ModelRepository(session)
    results = await repo.search(query=q, skip=skip, limit=limit)
    return results


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


@router.post("/", response_model=ModelResponse, status_code=201)
async def create_model(
    model_data: ModelCreate,
    session: AsyncSession = Depends(get_db),
) -> ModelResponse:
    """
    Create a new AI model.

    This endpoint creates a new model in the database after validating
    that no duplicate model names exist.

    Args:
        model_data: Model information (name, organization, description, etc.)

    Returns:
        The created model with generated ID and timestamps

    Raises:
        HTTPException 409: If a model with the same name already exists
        HTTPException 400: If input validation fails
        HTTPException 500: If database operation fails
    """
    repo = ModelRepository(session)

    # Check for duplicate model name
    existing = await repo.get_by_name(model_data.name)
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"Model with name '{model_data.name}' already exists with ID {existing.id}",
        )

    # Create the model
    try:
        new_model = Model(**model_data.model_dump())
        created = await repo.create(new_model)
        return created
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create model: {str(e)}",
        )


@router.patch("/{model_id}", response_model=ModelResponse)
async def update_model(
    model_id: int,
    model_data: ModelUpdate,
    session: AsyncSession = Depends(get_db),
) -> ModelResponse:
    """
    Update an existing AI model (partial update).

    Only fields provided in the request will be updated. All fields are optional.

    Args:
        model_id: The unique identifier of the model to update
        model_data: Fields to update (all optional)

    Returns:
        The updated model with new values

    Raises:
        HTTPException 404: If model with given ID doesn't exist
        HTTPException 409: If updating name would create duplicate
        HTTPException 400: If input validation fails
    """
    repo = ModelRepository(session)

    # Check if model exists
    existing = await repo.get_by_id(model_id)
    if not existing:
        raise HTTPException(
            status_code=404,
            detail=f"Model with id {model_id} not found",
        )

    # If updating name, check for duplicates (exclude current model)
    update_dict = model_data.model_dump(exclude_unset=True)
    if "name" in update_dict and update_dict["name"] != existing.name:
        duplicate = await repo.get_by_name(update_dict["name"])
        if duplicate:
            raise HTTPException(
                status_code=409,
                detail=f"Model with name '{update_dict['name']}' already exists with ID {duplicate.id}",
            )

    # Update the model with provided fields
    for field, value in update_dict.items():
        setattr(existing, field, value)

    try:
        updated = await repo.update(existing)
        return updated
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update model: {str(e)}",
        )


@router.delete("/{model_id}", status_code=204)
async def delete_model(
    model_id: int,
    session: AsyncSession = Depends(get_db),
) -> None:
    """
    Delete an AI model by ID.

    This is a hard delete - the model and all related records (benchmark results,
    opinions, use cases) will be permanently removed due to cascade delete.

    Args:
        model_id: The unique identifier of the model to delete

    Returns:
        No content (204 status code)

    Raises:
        HTTPException 404: If model with given ID doesn't exist
        HTTPException 409: If model cannot be deleted due to constraints
    """
    repo = ModelRepository(session)

    # Check if model exists
    existing = await repo.get_by_id(model_id)
    if not existing:
        raise HTTPException(
            status_code=404,
            detail=f"Model with id {model_id} not found",
        )

    try:
        await repo.delete(model_id)
        return None  # 204 No Content (no response body)
    except Exception as e:
        raise HTTPException(
            status_code=409,
            detail=f"Cannot delete model: {str(e)}",
        )


################################################
# Related resource endpoints
################################################


@router.get("/{model_id}/benchmarks", response_model=list[BenchmarkResultResponse])
async def get_model_benchmarks(
    model_id: int,
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        default=10, ge=1, le=1000, description="Maximum number of records to return"
    ),
    session: AsyncSession = Depends(get_db),
) -> Sequence[BenchmarkResultResponse]:
    """
    Get all benchmark results for a specific model.

    Returns the model's performance on all benchmarks it has been tested on.
    """
    # First check if model exists
    model_repo = ModelRepository(session)
    model = await model_repo.get_by_id(model_id)
    if not model:
        raise HTTPException(
            status_code=404, detail=f"Model with id {model_id} not found"
        )

    result_repo = BenchmarkResultRepository(session)
    results = await result_repo.get_by_model_id(model_id, skip=skip, limit=limit)
    return results


@router.get("/{model_id}/opinions", response_model=list[OpinionResponse])
async def get_model_opinions(
    model_id: int,
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        default=20, ge=1, le=100, description="Maximum number of records to return"
    ),
    session: AsyncSession = Depends(get_db),
) -> Sequence[OpinionResponse]:
    """
    Get all opinions for a specific model.

    Returns public opinions collected about this model from various sources.
    """
    # First check if model exists
    model_repo = ModelRepository(session)
    model = await model_repo.get_by_id(model_id)
    if not model:
        raise HTTPException(
            status_code=404, detail=f"Model with id {model_id} not found"
        )

    opinion_repo = OpinionRepository(session)
    opinions = await opinion_repo.get_by_model_id(model_id, limit=limit)
    return opinions


@router.get("/{model_id}/use-cases", response_model=list[UseCaseResponse])
async def get_model_use_cases(
    model_id: int,
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        default=20, ge=1, le=100, description="Maximum number of records to return"
    ),
    session: AsyncSession = Depends(get_db),
) -> Sequence[UseCaseResponse]:
    """
    Get all use cases for a specific model.

    Returns mentioned use cases for this model from various sources.
    """
    # First check if model exists
    model_repo = ModelRepository(session)
    model = await model_repo.get_by_id(model_id)
    if not model:
        raise HTTPException(
            status_code=404, detail=f"Model with id {model_id} not found"
        )

    use_case_repo = UseCaseRepository(session)
    use_cases = await use_case_repo.get_by_model_id(model_id, limit=limit)
    return use_cases
