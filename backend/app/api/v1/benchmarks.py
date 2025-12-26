"""
Benchmarks API Router

Provides REST endpoints for benchmark management:
- List benchmarks with pagination and filtering
- Get individual benchmark details
- Get benchmarks by category
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Sequence

from app.db import get_db
from app.db.repositories import BenchmarkRepository
from app.models.models import BenchmarkResponse

router = APIRouter(
    prefix="/api/v1/benchmarks",
    tags=["benchmarks"],
    responses={404: {"description": "Benchmark not found"}},
)


@router.get("/", response_model=list[BenchmarkResponse])
async def list_benchmarks(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, le=100),
    category: str | None = Query(default=None, description="Filter by category"),
    session: AsyncSession = Depends(get_db),
) -> Sequence[BenchmarkResponse]:
    """
    List all benchmarks with optional category filtering.

    - **skip**: Pagination offset
    - **limit**: Maximum results (max 100)
    - **category**: Optional category filter (e.g., "Knowledge", "Coding")
    """
    repo = BenchmarkRepository(session)

    if category:
        benchmarks = await repo.get_by_category(category, skip=skip, limit=limit)
    else:
        benchmarks = await repo.get_all(skip=skip, limit=limit)

    return benchmarks


@router.get("/categories", response_model=list[str])
async def list_categories(
    session: AsyncSession = Depends(get_db),
) -> Sequence[str]:
    """
    Get a list of all unique benchmark categories.

    Useful for populating category filter dropdowns in the frontend.
    """
    repo = BenchmarkRepository(session)
    categories = await repo.get_all_categories()
    return categories


@router.get("/{benchmark_id}", response_model=BenchmarkResponse)
async def get_benchmark(
    benchmark_id: int,
    session: AsyncSession = Depends(get_db),
) -> BenchmarkResponse:
    """
    Get a specific benchmark by ID.

    Raises:
        HTTPException 404: If benchmark doesn't exist
    """
    repo = BenchmarkRepository(session)
    benchmark = await repo.get_by_id(benchmark_id)

    if not benchmark:
        raise HTTPException(
            status_code=404, detail=f"Benchmark with id {benchmark_id} not found"
        )

    return benchmark
