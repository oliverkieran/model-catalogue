from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Sequence

from app.db.repository import BaseRepository
from app.models.models import UseCase


class UseCaseRepository(BaseRepository[UseCase]):
    """
    Repository for UseCase operations

    Inherits common CRUD from BaseRepository and adds use case-specific methods.
    """

    def __init__(self, session: AsyncSession):
        """Initialize with UseCase class and async session"""
        super().__init__(UseCase, session)

    async def get_by_model_id(
        self, model_id: int, limit: int = 100
    ) -> Sequence[UseCase]:
        """
        Get all use cases for a specific model.

        Args:
            model_id: The model's primary key
            limit: Maximum results

        Returns:
            Sequence of use cases

        Example:
            use_cases = await repo.get_by_model_id(1)
            for use_case in use_cases:
                print(f"{use_case.use_case}: {use_case.description}")
        """
        statement = select(UseCase).where(UseCase.model_id == model_id).limit(limit)

        result = await self.session.exec(statement)
        return result.all()

    async def get_by_use_case(self, use_case: str) -> Sequence[UseCase]:
        """
        Get all entries matching a specific use case.

        Args:
            use_case (str): The use case to search for.

        Returns:
            Sequence[UseCase]: A sequence of UseCase instances matching the use case.
        """
        statement = select(UseCase).where(UseCase.use_case == use_case)

        result = await self.session.exec(statement)
        return result.all()
