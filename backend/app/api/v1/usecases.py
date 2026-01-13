"""
UseCases API Router

Provides REST endpoints for managing mentioned use cases for AI models:
- List use cases with filtering by model_id
- Get individual use case details
- Create/Update/Delete use cases
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Sequence

from app.db import get_db
from app.db.repositories import UseCaseRepository, ModelRepository
from app.models.models import (
    UseCase,
    UseCaseCreate,
    UseCaseUpdate,
    UseCaseResponse,
)

router = APIRouter(
    prefix="/api/v1/use-cases",
    tags=["use-cases"],
    responses={404: {"description": "Use case not found"}},
)


@router.get("/", response_model=list[UseCaseResponse])
async def list_use_cases(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, le=100),
    model_id: int | None = Query(default=None, description="Filter by model ID"),
    session: AsyncSession = Depends(get_db),
) -> Sequence[UseCaseResponse]:
    """
    List use cases with optional filtering.

    - **skip**: Pagination offset
    - **limit**: Maximum results (max 100)
    - **model_id**: Optional filter by model ID
    """
    repo = UseCaseRepository(session)

    if model_id:
        use_cases = await repo.get_by_model_id(model_id, limit=limit)
    else:
        use_cases = await repo.get_all(skip=skip, limit=limit)

    return use_cases


@router.get("/{use_case_id}", response_model=UseCaseResponse)
async def get_use_case(
    use_case_id: int,
    session: AsyncSession = Depends(get_db),
) -> UseCaseResponse:
    """
    Get a specific use case by ID.

    Raises:
        HTTPException 404: If use case doesn't exist
    """
    repo = UseCaseRepository(session)
    use_case = await repo.get_by_id(use_case_id)

    if not use_case:
        raise HTTPException(
            status_code=404, detail=f"Use case with id {use_case_id} not found"
        )

    return use_case


@router.post("/", response_model=UseCaseResponse, status_code=201)
async def create_use_case(
    use_case_data: UseCaseCreate,
    session: AsyncSession = Depends(get_db),
) -> UseCaseResponse:
    """
    Create a new use case.

    Validates that the referenced model exists before creation.

    Raises:
        HTTPException 404: If referenced model doesn't exist
        HTTPException 500: If database operation fails
    """
    # Validate model exists
    model_repo = ModelRepository(session)
    model = await model_repo.get_by_id(use_case_data.model_id)
    if not model:
        raise HTTPException(
            status_code=404, detail=f"Model with id {use_case_data.model_id} not found"
        )

    try:
        repo = UseCaseRepository(session)
        new_use_case = UseCase(**use_case_data.model_dump())
        created = await repo.create(new_use_case)
        return created
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to create use case: {str(e)}"
        )


@router.patch("/{use_case_id}", response_model=UseCaseResponse)
async def update_use_case(
    use_case_id: int,
    use_case_data: UseCaseUpdate,
    session: AsyncSession = Depends(get_db),
) -> UseCaseResponse:
    """
    Update an existing use case (partial update).

    Only fields provided in the request will be updated.

    Raises:
        HTTPException 404: If use case doesn't exist
        HTTPException 500: If database operation fails
    """
    repo = UseCaseRepository(session)

    # Check if use case exists
    existing = await repo.get_by_id(use_case_id)
    if not existing:
        raise HTTPException(
            status_code=404, detail=f"Use case with id {use_case_id} not found"
        )

    # Apply updates
    update_dict = use_case_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(existing, field, value)

    try:
        updated = await repo.update(existing)
        return updated
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to update use case: {str(e)}"
        )


@router.delete("/{use_case_id}", status_code=204)
async def delete_use_case(
    use_case_id: int,
    session: AsyncSession = Depends(get_db),
):
    """
    Delete a use case by ID.

    Raises:
        HTTPException 404: If use case doesn't exist
        HTTPException 409: If delete operation fails
    """
    repo = UseCaseRepository(session)

    # Check if use case exists
    existing = await repo.get_by_id(use_case_id)
    if not existing:
        raise HTTPException(
            status_code=404, detail=f"Use case with id {use_case_id} not found"
        )

    try:
        await repo.delete(use_case_id)
        return None
    except Exception as e:
        raise HTTPException(status_code=409, detail=f"Cannot delete use case: {str(e)}")
