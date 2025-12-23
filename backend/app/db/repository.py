"""
Base Repository Pattern Implementation for SQLModel

Provides a generic base class for all repositories with common CRUD operations.
All repositories inherit from this base and add domain-specific methods as needed.
"""

from typing import TypeVar, Generic, Sequence
from sqlmodel import SQLModel, select, func
from sqlmodel.ext.asyncio.session import AsyncSession

# Type variable bound to SQLModel for generic repository
ModelType = TypeVar("ModelType", bound=SQLModel)


class BaseRepository(Generic[ModelType]):
    """
    Generic async repository providing CRUD operations for any SQLModel table.

    Usage:
        class ModelRepository(BaseRepository[Model]):
            def __init__(self, session: AsyncSession):
                super().__init__(Model, session)

            # Add domain-specific methods here
    """

    def __init__(self, model: type[ModelType], session: AsyncSession):
        """
        Initialize repository with a model class and database session.

        Args:
            model: The SQLModel class this repository manages (e.g. Model, Benchmark)
            session: Async database session for executing queries
        """
        self.model = model
        self.session = session

    async def get_by_id(self, id: int) -> ModelType | None:
        """
        Retrieve a record by its primary key ID.

        Args:
            id: Primary key of the record to retrieve

        Returns:
            The record instance if found, else None

        Example:
            model = await repository.get_by_id(1)
            if model:
                print(f"Found: {model.name}")
        """
        return await self.session.get(self.model, id)

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        order_by: str | None = None,
    ) -> Sequence[ModelType]:
        """
        Retrieve multiple records with pagination and optional ordering.

        Args:
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return
            order_by: Column name to order by (optional)

        Returns:
            Sequence of record instances

        Example:
            # Get models 10-20, ordered by creation date
            models = await repository.get_all(skip=10, limit=10, order_by="created_at")
        """
        statement = select(self.model).offset(skip).limit(limit)
        if order_by:
            # Get the column from the model
            order_column = getattr(self.model, order_by, None)
            if order_column is not None:
                statement = statement.order_by(order_column)

        result = await self.session.exec(statement)
        return result.all()

    async def create(self, entity: ModelType) -> ModelType:
        """
        Create a new entity/record in the database.

        Args:
            entity: The entity to create (should not have an id)

        Returns:
            The created entity with id and timestamps populated

        Raises:
            ValueError: If the entity already has an ID (should use update instead)

        Example:
            new_model = Model(name="gpt-5", display_name="GPT-5", organization="OpenAI")
            created_model = await repository.create(new_model)
            print(f"Created model with ID: {created_model.id}")
        """
        # Validate that this is a new entity
        if hasattr(entity, "id") and entity.id is not None:
            raise ValueError(
                f"Cannot create entity that already has an ID ({entity.id}). "
                "Use update() instead."
            )

        self.session.add(entity)
        await self.session.commit()
        await self.session.refresh(entity)
        return entity

    async def update(self, entity: ModelType) -> ModelType:
        """
        Update an existing entity in the database.

        This method uses merge() to update the entity, which ensures that
        the entity is properly tracked by the session and handles both
        attached and detached entities correctly.

        Args:
            entity: The entity to update (must have an id)

        Returns:
            The updated entity

        Raises:
            ValueError: If the entity doesn't have an ID or doesn't exist in the database

        Example:
            model = await repository.get_by_id(1)
            model.name = "GPT-4 Turbo"
            updated = await repository.update(model)
        """
        # Validate that the entity has an ID
        if not hasattr(entity, "id") or entity.id is None:
            raise ValueError(
                "Cannot update entity without an ID. Use create() for new entities."
            )

        # Verify the entity exists in the database
        existing = await self.get_by_id(entity.id)
        if existing is None:
            raise ValueError(
                f"Cannot update entity with ID {entity.id}: not found in database."
            )

        # Use merge to update the entity (handles both attached and detached entities)
        merged_entity = await self.session.merge(entity)
        await self.session.commit()
        await self.session.refresh(merged_entity)
        return merged_entity

    async def delete(self, id: int) -> bool:
        """
        Delete an entity by its primary key.

        Args:
            id: Primary key of the entity to delete

        Returns:
            True if entity was deleted, False if not found

        Example:
            deleted = await repository.delete(1)
            if deleted:
                print("Model deleted successfully")
        """
        entity = await self.get_by_id(id)
        if entity:
            await self.session.delete(entity)
            await self.session.commit()
            return True
        return False

    async def exists(self, id: int) -> bool:
        """
        Check if an entity exists by its primary key.

        Args:
            id: Primary key to check

        Returns:
            True if entity exists, False otherwise

        Example:
            if await repository.exists(1):
                print("Model exists")
        """
        entity = await self.get_by_id(id)
        return entity is not None

    async def count(self) -> int:
        """
        Count total number of entities in the table.

        Returns:
            Total count

        Example:
            total = await repository.count()
            print(f"Total models: {total}")
        """
        statement = select(func.count()).select_from(self.model)
        result = await self.session.exec(statement)
        return result.one()

    async def get_multi_by_ids(self, ids: list[int]) -> Sequence[ModelType]:
        """
        Retrieve multiple entities by their primary keys.

        Args:
            ids: List of primary keys

        Returns:
            Sequence of found entities (may be fewer than requested if some don't exist)

        Example:
            models = await repository.get_multi_by_ids([1, 2, 3])
        """
        statement = select(self.model).where(self.model.id.in_(ids))
        result = await self.session.exec(statement)
        return result.all()
