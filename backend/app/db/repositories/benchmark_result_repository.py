"""
Repository for BenchmarkResult entity

Handles the many-to-many relationship between Models and Benchmarks with scores.
"""

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import selectinload
from typing import Sequence
from datetime import date

from app.models.models import BenchmarkResult, Model, Benchmark
from app.db.repository import BaseRepository


class BenchmarkResultRepository(BaseRepository[BenchmarkResult]):
    """Repository for BenchmarkResult operations"""

    def __init__(self, session: AsyncSession):
        super().__init__(BenchmarkResult, session)

    async def get_by_model_id(
        self, model_id: int, skip: int = 0, limit: int = 100
    ) -> Sequence[BenchmarkResult]:
        """
        Get all benchmark results for a specific model.

        Args:
            model_id: The model's primary key
            skip: Pagination offset
            limit: Maximum results

        Returns:
            Sequence of benchmark results

        Example:
            results = await repo.get_by_model_id(1)
            for result in results:
                print(f"{result.benchmark.name}: {result.score}")
        """
        statement = (
            select(BenchmarkResult)
            .where(BenchmarkResult.model_id == model_id)
            .options(selectinload(BenchmarkResult.benchmark))
            .offset(skip)
            .limit(limit)
        )

        result = await self.session.exec(statement)
        return result.all()

    async def get_by_benchmark_id(
        self, benchmark_id: int, skip: int = 0, limit: int = 100
    ) -> Sequence[BenchmarkResult]:
        """
        Get all results for a specific benchmark (across all models).

        Args:
            benchmark_id: The benchmark's primary key
            skip: Pagination offset
            limit: Maximum results

        Returns:
            Sequence of benchmark results

        Example:
            results = await repo.get_by_benchmark_id(1)
            # Get all model scores on MMLU
        """
        statement = (
            select(BenchmarkResult)
            .where(BenchmarkResult.benchmark_id == benchmark_id)
            .options(selectinload(BenchmarkResult.model))  # Eager load model
            .offset(skip)
            .limit(limit)
            .order_by(BenchmarkResult.score.desc())  # Highest scores first
        )

        result = await self.session.exec(statement)
        return result.all()

    async def get_by_model_and_benchmark(
        self, model_id: int, benchmark_id: int
    ) -> Sequence[BenchmarkResult]:
        """
        Get all results for a specific model-benchmark pair.

        Note: Returns a sequence because the same model may have been tested
        on the same benchmark multiple times (different dates).

        Args:
            model_id: The model's primary key
            benchmark_id: The benchmark's primary key

        Returns:
            Sequence of matching results

        Example:
            results = await repo.get_by_model_and_benchmark(1, 5)
            # Get all GPT-4 scores on MMLU over time
        """
        statement = select(BenchmarkResult).where(
            BenchmarkResult.model_id == model_id,
            BenchmarkResult.benchmark_id == benchmark_id,
        )

        result = await self.session.exec(statement)
        return result.all()

    async def result_exists(
        self,
        model_id: int,
        benchmark_id: int,
        date_tested: date | None = None,
    ) -> bool:
        """
        Check if a result already exists for this model-benchmark-date combination.

        Respects the unique constraint on (model_id, benchmark_id, date_tested).

        Args:
            model_id: The model's primary key
            benchmark_id: The benchmark's primary key
            date_tested: Optional test date

        Returns:
            True if result exists, False otherwise

        Example:
            # Before inserting
            if await repo.result_exists(1, 5, date(2024, 1, 15)):
                raise ValueError("Result already recorded for this date")
        """
        statement = select(BenchmarkResult).where(
            BenchmarkResult.model_id == model_id,
            BenchmarkResult.benchmark_id == benchmark_id,
            BenchmarkResult.date_tested == date_tested,
        )

        result = await self.session.exec(statement)
        return result.first() is not None
