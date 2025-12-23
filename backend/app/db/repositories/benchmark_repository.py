"""
Repository for Benchmark entity

Provides database operations for the Benchmark table.
"""

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Sequence

from app.models.models import Benchmark
from app.db.repository import BaseRepository


class BenchmarkRepository(BaseRepository[Benchmark]):
    """Repository for Benchmark operations"""

    def __init__(self, session: AsyncSession):
        super().__init__(Benchmark, session)

    async def get_by_name(self, name: str) -> Benchmark | None:
        """Get benchmark by unique name"""
        statement = select(Benchmark).where(Benchmark.name == name)
        result = await self.session.exec(statement)
        return result.first()

    async def get_by_category(
        self, category: str, skip: int = 0, limit: int = 100
    ) -> Sequence[Benchmark]:
        """
        Get all benchmarks in a specific category.

        Args:
            category: Benchmark category (e.g., "Knowledge", "Coding", "Math")
            skip: Pagination offset
            limit: Maximum results

        Returns:
            Sequence of benchmarks in that category

        Example:
            coding_benchmarks = await repo.get_by_category("Coding")
            # Returns: HumanEval, MBPP, CodeContests, etc.
        """
        statement = (
            select(Benchmark)
            .where(Benchmark.category == category)
            .offset(skip)
            .limit(limit)
        )

        result = await self.session.exec(statement)
        return result.all()

    async def get_all_categories(self) -> Sequence[str]:
        """
        Get list of unique benchmark categories.

        Returns:
            Sequence of category names

        Example:
            categories = await repo.get_all_categories()
            # Returns: ["Knowledge", "Coding", "Math", "Reasoning", ...]
        """
        statement = select(Benchmark.category).distinct()
        result = await self.session.exec(statement)
        return result.all()

    async def name_exists(self, name: str, exclude_id: int | None = None) -> bool:
        """Check if a benchmark name already exists"""
        statement = select(Benchmark).where(Benchmark.name == name)

        if exclude_id is not None:
            statement = statement.where(Benchmark.id != exclude_id)

        result = await self.session.exec(statement)
        return result.first() is not None
