from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Sequence

from app.db.repository import BaseRepository
from app.models.models import Opinion


class OpinionRepository(BaseRepository[Opinion]):
    """
    Repository for Opinion operations

    Inherits common CRUD from BaseRepository and adds opinion-specific methods.
    """

    def __init__(self, session: AsyncSession):
        """Initialize with Opinion class and async session"""
        super().__init__(Opinion, session)

    async def get_by_model_id(
        self, model_id: int, limit: int = 100
    ) -> Sequence[Opinion]:
        """
        Get all opinion on a specific model.

        Args:
            model_id: The model's primary key
            limit: Maximum results

        Returns:
            Sequence of opinions

        Example:
            opinions = await repo.get_by_model_id(1)
            for opinion in opinions:
                print(f"{opinion.source}: {opinion.content}")
        """
        statement = select(Opinion).where(Opinion.model_id == model_id).limit(limit)

        result = await self.session.exec(statement)
        return result.all()

    async def get_by_sentiment(self, sentiment: str) -> Sequence[Opinion]:
        """
        Get all opinions with a specific sentiment.

        Args:
            sentiment: The sentiment to filter by (e.g., "positive", "negative", "neutral")

        Returns:
            Sequence of opinions with the specified sentiment

        Example:
            positive_opinions = await repo.get_by_sentiment("positive")
            for opinion in positive_opinions:
                print(f"{opinion.source}: {opinion.content}")
        """
        statement = select(Opinion).where(Opinion.sentiment == sentiment)
        result = await self.session.exec(statement)
        return result.all()

    async def search_by_content(self, query: str) -> Sequence[Opinion]:
        """
        Search opinions by content (case-insensitive).

        Args:
            query: Search term

        Returns:
            Sequence of matching opinions

        Example:
            results = await repo.search_by_content("great model")
            for opinion in results:
                print(f"{opinion.source}: {opinion.content}")
        """
        search_pattern = f"%{query}%"
        statement = select(Opinion).where(Opinion.content.ilike(search_pattern))

        result = await self.session.exec(statement)
        return result.all()
