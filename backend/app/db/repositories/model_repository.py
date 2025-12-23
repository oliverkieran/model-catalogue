"""
Repository for AI Model entity

Provides CRUD operations for AI Model intances with domain-specific queries.
"""

from sqlmodel import select, or_
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Sequence

from app.models.models import Model
from app.db.repository import BaseRepository


class ModelRepository(BaseRepository[Model]):
    """
    Repository for AI Model operations.

    Inherits common CRUD from BaseRepository and adds model-specific methods.
    """

    def __init__(self, session: AsyncSession):
        """Initialize with Model class and async session"""
        super().__init__(Model, session)

    async def get_by_name(self, name: str) -> Model | None:
        """
        Retrieve a model by its unique name.

        Args:
            name: The model name (e.g., "gpt-4", "claude-3-opus")

        Returns:
            Model if found, None otherwise

        Example:
            model = await repo.get_by_name("gpt-4")
        """
        statement = select(Model).where(Model.name == name)
        result = await self.session.exec(statement)
        return result.first()

    async def search(
        self, query: str, skip: int = 0, limit: int = 100
    ) -> Sequence[Model]:
        """
        Search models by name or organization (case-insensitive).

        Args:
            query: Search term
            skip: Pagination offset
            limit: Maximum results

        Returns:
            Sequence of matching models

        Example:
            results = await repo.search("openai")
            # Returns: GPT-4, GPT-3.5, DALL-E, etc.
        """
        search_pattern = f"%{query}%"
        statement = (
            select(Model)
            .where(
                or_(
                    Model.name.ilike(search_pattern),
                    Model.name.ilike(search_pattern),
                    Model.organization.ilike(search_pattern),
                )
            )
            .offset(skip)
            .limit(limit)
        )

        result = await self.session.exec(statement)
        return result.all()

    async def get_by_organization(
        self, organization: str, skip: int = 0, limit: int = 100
    ) -> Sequence[Model]:
        """
        Retrieve all models from a specific organization.

        Args:
            organization: Organization name (e.g., "OpenAI")
            skip: Pagination offset
            limit: Maximum results

        Returns:
            Sequence of models from that organization

        Example:
            openai_models = await repo.get_by_organization("OpenAI")
        """
        statement = (
            select(Model)
            .where(Model.organization == organization)
            .offset(skip)
            .limit(limit)
            .order_by(Model.release_date.desc())
        )

        result = await self.session.exec(statement)
        return result.all()

    async def name_exists(self, name: str, exclude_id: int | None = None) -> bool:
        """
        Check if a model name already exists.

        Useful for validation before creating/updating models.

        Args:
            name: Model name to check
            exclude_id: Optional ID to exclude (for updates)

        Returns:
            True if name exists, False otherwise

        Example:
            # Before creating
            if await repo.name_exists("gpt-4"):
                raise ValueError("Model already exists")

            # Before updating (exclude current model)
            if await repo.name_exists("gpt-4", exclude_id=current_model.id):
                raise ValueError("Name already taken by another model")
        """
        statement = select(Model).where(Model.name == name)

        # Exclude ID if provided
        if exclude_id is not None:
            statement = statement.where(Model.id != exclude_id)

        result = await self.session.exec(statement)
        return result.first() is not None
