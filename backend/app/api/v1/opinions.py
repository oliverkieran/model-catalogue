"""
Opinions API Router

Provides REST endpoints for managing public opinions about AI models:
- List opinions with filtering by model_id and sentiment
- Search opinions by content
- Get individual opinion details
- Create/Update/Delete opinions
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Sequence

from app.db import get_db
from app.db.repositories import OpinionRepository, ModelRepository
from app.models.models import (
    Opinion,
    OpinionCreate,
    OpinionUpdate,
    OpinionResponse,
)

router = APIRouter(
    prefix="/api/v1/opinions",
    tags=["opinions"],
    responses={404: {"description": "Opinion not found"}},
)


@router.get("/", response_model=list[OpinionResponse])
async def list_opinions(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, le=100),
    model_id: int | None = Query(default=None, description="Filter by model ID"),
    sentiment: str | None = Query(default=None, description="Filter by sentiment"),
    session: AsyncSession = Depends(get_db),
) -> Sequence[OpinionResponse]:
    """
    List opinions with optional filtering.

    - **skip**: Pagination offset
    - **limit**: Maximum results (max 100)
    - **model_id**: Optional filter by model ID
    - **sentiment**: Optional filter by sentiment (e.g., "positive", "negative", "neutral")
    """
    repo = OpinionRepository(session)

    if model_id:
        opinions = await repo.get_by_model_id(model_id, limit=limit)
    elif sentiment:
        opinions = await repo.get_by_sentiment(sentiment)
    else:
        opinions = await repo.get_all(skip=skip, limit=limit)

    return opinions


@router.get("/search/", response_model=list[OpinionResponse])
async def search_opinions(
    q: str = Query(
        ..., min_length=2, description="Search query (minimum 2 characters)"
    ),
    session: AsyncSession = Depends(get_db),
) -> Sequence[OpinionResponse]:
    """
    Search opinions by content (case-insensitive).

    - **q**: Search term to find in opinion content
    """
    repo = OpinionRepository(session)
    results = await repo.search_by_content(q)
    return results


@router.get("/{opinion_id}", response_model=OpinionResponse)
async def get_opinion(
    opinion_id: int,
    session: AsyncSession = Depends(get_db),
) -> OpinionResponse:
    """
    Get a specific opinion by ID.

    Raises:
        HTTPException 404: If opinion doesn't exist
    """
    repo = OpinionRepository(session)
    opinion = await repo.get_by_id(opinion_id)

    if not opinion:
        raise HTTPException(
            status_code=404, detail=f"Opinion with id {opinion_id} not found"
        )

    return opinion


@router.post("/", response_model=OpinionResponse, status_code=201)
async def create_opinion(
    opinion_data: OpinionCreate,
    session: AsyncSession = Depends(get_db),
) -> OpinionResponse:
    """
    Create a new opinion.

    Validates that the referenced model exists before creation.

    Raises:
        HTTPException 404: If referenced model doesn't exist
        HTTPException 500: If database operation fails
    """
    # Validate model exists
    model_repo = ModelRepository(session)
    model = await model_repo.get_by_id(opinion_data.model_id)
    if not model:
        raise HTTPException(
            status_code=404, detail=f"Model with id {opinion_data.model_id} not found"
        )

    try:
        repo = OpinionRepository(session)
        new_opinion = Opinion(**opinion_data.model_dump())
        created = await repo.create(new_opinion)
        return created
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to create opinion: {str(e)}"
        )


@router.patch("/{opinion_id}", response_model=OpinionResponse)
async def update_opinion(
    opinion_id: int,
    opinion_data: OpinionUpdate,
    session: AsyncSession = Depends(get_db),
) -> OpinionResponse:
    """
    Update an existing opinion (partial update).

    Only fields provided in the request will be updated.

    Raises:
        HTTPException 404: If opinion doesn't exist
        HTTPException 500: If database operation fails
    """
    repo = OpinionRepository(session)

    # Check if opinion exists
    existing = await repo.get_by_id(opinion_id)
    if not existing:
        raise HTTPException(
            status_code=404, detail=f"Opinion with id {opinion_id} not found"
        )

    # Apply updates
    update_dict = opinion_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(existing, field, value)

    try:
        updated = await repo.update(existing)
        return updated
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to update opinion: {str(e)}"
        )


@router.delete("/{opinion_id}", status_code=204)
async def delete_opinion(
    opinion_id: int,
    session: AsyncSession = Depends(get_db),
):
    """
    Delete an opinion by ID.

    Raises:
        HTTPException 404: If opinion doesn't exist
        HTTPException 409: If delete operation fails
    """
    repo = OpinionRepository(session)

    # Check if opinion exists
    existing = await repo.get_by_id(opinion_id)
    if not existing:
        raise HTTPException(
            status_code=404, detail=f"Opinion with id {opinion_id} not found"
        )

    try:
        await repo.delete(opinion_id)
        return None
    except Exception as e:
        raise HTTPException(status_code=409, detail=f"Cannot delete opinion: {str(e)}")
