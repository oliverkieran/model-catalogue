"""
Benchmark Results API Endpoints

Provides REST endpoints for managing model performance  on benchmarks.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Sequence

from app.db import get_db
from app.db.repositories import (
    BenchmarkResultRepository,
    ModelRepository,
    BenchmarkRepository,
)
from app.models.models import (
    BenchmarkResult,
    BenchmarkResultCreate,
    BenchmarkResultUpdate,
    BenchmarkResultResponse,
)

router = APIRouter(
    prefix="/api/v1/benchmark-results",
    tags=["benchmark-results"],
    responses={404: {"description": "Benchmark result not found"}},
)


@router.get("/", response_model=list[BenchmarkResultResponse])
async def list_benchmark_results(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, le=10000),
    model_id: int | None = Query(default=None, description="Filter by model ID"),
    benchmark_id: int | None = Query(
        default=None, description="Filter by benchmark ID"
    ),
    session: AsyncSession = Depends(get_db),
) -> Sequence[BenchmarkResultResponse]:
    """
    List benchmark results with optional filtering.

    Can filter by model_id, benchmark_id, or both.
    """
    repo = BenchmarkResultRepository(session)

    # Apply filters based on query parameters
    if model_id and benchmark_id:
        # Get results for specific model+benchmark combination
        results = await repo.get_by_model_and_benchmark(
            model_id=model_id,
            benchmark_id=benchmark_id,
        )
    elif model_id:
        # Get all results for a model
        results = await repo.get_by_model_id(model_id, skip=skip, limit=limit)
    elif benchmark_id:
        # Get all results for a benchmark
        results = await repo.get_by_benchmark_id(benchmark_id, skip=skip, limit=limit)
    else:
        # Get all results
        results = await repo.get_all(skip=skip, limit=limit)

    return results


@router.get("/{result_id}", response_model=BenchmarkResultResponse)
async def get_benchmark_result(
    result_id: int,
    session: AsyncSession = Depends(get_db),
) -> BenchmarkResultResponse:
    """Get a specific benchmark result by ID."""
    repo = BenchmarkResultRepository(session)
    result = await repo.get_by_id(result_id)

    if not result:
        raise HTTPException(
            status_code=404, detail=f"Benchmark result with id {result_id} not found"
        )

    return result


@router.post("/", response_model=BenchmarkResultResponse, status_code=201)
async def create_benchmark_result(
    result_data: BenchmarkResultCreate,
    session: AsyncSession = Depends(get_db),
) -> BenchmarkResultResponse:
    """
    Create a new benchmark result.

    Validates that:
    - Model exists
    - Benchmark exists
    - No duplicate result for same model+benchmark+date
    """
    # Validate model exists
    model_repo = ModelRepository(session)
    model = await model_repo.get_by_id(result_data.model_id)
    if not model:
        raise HTTPException(
            status_code=404, detail=f"Model with id {result_data.model_id} not found"
        )

    # Validate benchmark exists
    benchmark_repo = BenchmarkRepository(session)
    benchmark = await benchmark_repo.get_by_id(result_data.benchmark_id)
    if not benchmark:
        raise HTTPException(
            status_code=404,
            detail=f"Benchmark with id {result_data.benchmark_id} not found",
        )

    # Check for duplicate (same model+benchmark+date)
    result_repo = BenchmarkResultRepository(session)
    if result_data.date_tested:
        exists = await result_repo.result_exists(
            model_id=result_data.model_id,
            benchmark_id=result_data.benchmark_id,
            date_tested=result_data.date_tested,
        )
        if exists:
            raise HTTPException(
                status_code=409,
                detail=(
                    f"Result for model {result_data.model_id} on benchmark "
                    f"{result_data.benchmark_id} dated {result_data.date_tested} already exists"
                ),
            )

    try:
        new_result = BenchmarkResult(**result_data.model_dump())
        created = await result_repo.create(new_result)
        return created
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to create benchmark result: {str(e)}"
        )


@router.patch("/{result_id}", response_model=BenchmarkResultResponse)
async def update_benchmark_result(
    result_id: int,
    result_data: BenchmarkResultUpdate,
    session: AsyncSession = Depends(get_db),
) -> BenchmarkResultResponse:
    """
    Update an existing benchmark result (partial update).

    Note: Cannot update model_id or benchmark_id (would break relationships).
    """
    repo = BenchmarkResultRepository(session)

    # Check if result exists
    existing = await repo.get_by_id(result_id)
    if not existing:
        raise HTTPException(
            status_code=404, detail=f"Benchmark result with id {result_id} not found"
        )

    # Apply updates
    update_dict = result_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(existing, field, value)

    try:
        updated = await repo.update(existing)
        return updated
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to update benchmark result: {str(e)}"
        )


@router.delete("/{result_id}", status_code=204)
async def delete_benchmark_result(
    result_id: int,
    session: AsyncSession = Depends(get_db),
):
    """Delete a benchmark result by ID."""
    repo = BenchmarkResultRepository(session)

    # Check if result exists
    existing = await repo.get_by_id(result_id)
    if not existing:
        raise HTTPException(
            status_code=404, detail=f"Benchmark result with id {result_id} not found"
        )

    try:
        await repo.delete(result_id)
        return None
    except Exception as e:
        raise HTTPException(
            status_code=409, detail=f"Cannot delete benchmark result: {str(e)}"
        )
