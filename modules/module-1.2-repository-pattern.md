# Module 1.2: Repository Pattern with SQLModel - Abstracting Data Access

**Duration:** 2 hours
**Difficulty:** Intermediate
**Prerequisites:** Module 1.1 complete, understanding of async/await in Python

---

## Introduction: Why Separate Data Access from Business Logic?

You've designed a solid database schema with SQLModel. Now comes a crucial architectural decision: how should the rest of your application interact with the database?

You could scatter database queries throughout your codebase:

```python
# ❌ Bad: Database logic mixed with API endpoint
@app.get("/api/v1/models/{id}")
async def get_model(id: int):
    async with AsyncSessionLocal() as session:
        statement = select(Model).where(Model.id == id)
        result = await session.execute(statement)
        model = result.scalar_one_or_none()
        if not model:
            raise HTTPException(status_code=404)
        return model
```

This approach has serious problems:

- **Code duplication**: Every endpoint that needs a model by ID rewrites the same query
- **Hard to test**: Can't test business logic without a real database
- **Difficult to change**: Want to add caching? You'll need to modify 20+ endpoints
- **Violates Single Responsibility**: Endpoints should handle HTTP, not database details
- **Makes debugging harder**: Database code scattered everywhere

**The Repository Pattern** solves these problems by centralizing all database operations in dedicated classes. Think of repositories as specialized librarians—each knows everything about finding, storing, and organizing one type of entity.

In this module, you'll learn to:

- **Separate concerns** cleanly: repositories handle data, services handle business logic, endpoints handle HTTP
- **Write testable code** by mocking repositories instead of databases
- **Build reusable abstractions** that eliminate code duplication
- **Master async patterns** in Python with context managers and async generators
- **Apply SOLID principles** in a practical, real-world context

This is one of the most valuable patterns in enterprise software development. Master it here, and you'll use it in every project going forward.

---

## What You'll Build

By the end of this module, you'll have:

- ✅ A `BaseRepository` class with async CRUD operations using SQLModel
- ✅ Specific repository classes for each entity (`ModelRepository`, `BenchmarkRepository`, etc.)
- ✅ Type-safe query methods leveraging SQLModel's `select()` function
- ✅ Proper async session management with context managers
- ✅ Comprehensive unit tests for all repository methods
- ✅ Understanding of dependency injection patterns for FastAPI
- ✅ A foundation for the service layer (Module 2.x)

---

## Understanding the Repository Pattern

Before we code, let's understand the pattern conceptually.

### The Three-Layer Architecture

Professional applications separate concerns into layers:

```
┌─────────────────────────────────────────┐
│         API Layer (Endpoints)           │  ← Handles HTTP: routing, validation, responses
│  @app.get("/models")                    │
│  async def get_models(...)              │
└─────────────────┬───────────────────────┘
                  │ depends on
┌─────────────────▼───────────────────────┐
│      Service Layer (Business Logic)     │  ← Orchestrates: combines repos, applies rules
│  class ModelService:                    │
│    def create_with_validation(...)      │
└─────────────────┬───────────────────────┘
                  │ depends on
┌─────────────────▼───────────────────────┐
│   Repository Layer (Data Access)        │  ← Database: queries, transactions, persistence
│  class ModelRepository:                 │
│    async def get_by_id(...)             │
└─────────────────┬───────────────────────┘
                  │ uses
┌─────────────────▼───────────────────────┐
│          Database (PostgreSQL)          │
└─────────────────────────────────────────┘
```

**Key insight:** Each layer only knows about the layer directly below it. The API layer never talks to the database directly.

### The Repository Interface

A repository provides a **collection-like interface** to your database:

```python
# Instead of thinking about SQL...
SELECT * FROM models WHERE id = 5;

# You think about collections...
model = await model_repository.get_by_id(5)
```

Common repository methods:

- **get_by_id(id)** - Fetch a single entity
- **get_all(skip, limit)** - Fetch multiple entities with pagination
- **create(entity)** - Add a new entity
- **update(id, entity)** - Modify an existing entity
- **delete(id)** - Remove an entity
- **exists(id)** - Check if entity exists
- **count()** - Count total entities

Plus domain-specific methods:

- `ModelRepository.get_by_name(name)`
- `ModelRepository.search(query)`
- `BenchmarkRepository.get_by_category(category)`

### Benefits of the Repository Pattern

1. **Testability**: Mock repositories in tests without touching the database
2. **Consistency**: All database operations follow the same patterns
3. **Maintainability**: Change database logic in one place
4. **Flexibility**: Swap implementations (SQL → NoSQL, add caching layer)
5. **Clarity**: Reading the code reveals intent, not SQL details

**Real-world scenario:** Imagine you need to add Redis caching to all `get_by_id` calls. With repositories, you modify one method in `BaseRepository`. Without them, you'd hunt through hundreds of endpoints.

**🎯 Checkpoint:** Understand that repositories abstract the "how" of data access, exposing only the "what."

---

## Step 1: Creating the Base Repository

We'll start with a `BaseRepository` class that provides common CRUD operations for any entity.

### Understanding Generic Types in Python

Our base repository will work with any SQLModel table. We'll use Python's **generic types** to achieve this:

```python
from typing import TypeVar, Generic

# Define a type variable that must be a SQLModel
ModelType = TypeVar("ModelType", bound=SQLModel)

class BaseRepository(Generic[ModelType]):
    def __init__(self, model: type[ModelType]):
        self.model = model  # Store the model class (e.g., Model, Benchmark)
```

**What this means:**

- `Generic[ModelType]` makes the class generic over a type
- When you create `BaseRepository[Model]()`, `ModelType` becomes `Model`
- The repository knows what type it's working with, giving you type hints everywhere

### Create the Base Repository

Create `backend/app/db/repository.py`:

```python
"""
Base Repository Pattern Implementation for SQLModel

Provides a generic base class for all repositories with common CRUD operations.
All repositories inherit from this base and add domain-specific methods.
"""

from typing import TypeVar, Generic, Any, Sequence
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
            model: The SQLModel class this repository manages (e.g., Model, Benchmark)
            session: Async database session for executing queries
        """
        self.model = model
        self.session = session

    async def get_by_id(self, id: int) -> ModelType | None:
        """
        Retrieve a single entity by its primary key.

        Args:
            id: Primary key value

        Returns:
            Entity if found, None otherwise

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
        Retrieve multiple entities with pagination.

        Args:
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return
            order_by: Column name to order by (optional)

        Returns:
            Sequence of entities

        Example:
            # Get models 10-20, ordered by creation date
            models = await repository.get_all(skip=10, limit=10, order_by="created_at")
        """
        statement = select(self.model).offset(skip).limit(limit)

        # Add ordering if specified
        if order_by:
            # Get the column from the model
            order_column = getattr(self.model, order_by, None)
            if order_column is not None:
                statement = statement.order_by(order_column)

        result = await self.session.exec(statement)
        return result.all()

    async def create(self, entity: ModelType) -> ModelType:
        """
        Create a new entity in the database.

        Args:
            entity: The entity to create (should not have an id)

        Returns:
            The created entity with id and timestamps populated

        Raises:
            ValueError: If the entity already has an ID (should use update instead)

        Example:
            new_model = Model(name="GPT-5", organization="OpenAI")
            created = await repository.create(new_model)
            print(f"Created with ID: {created.id}")
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
```

**Let's break down the key concepts:**

### Understanding create() vs update()

You might wonder why `create()` and `update()` appear similar—both use sessions and commits. However, they have important differences:

**create() method:**
- **Validates** the entity doesn't have an ID (ensuring it's new)
- Uses `session.add()` to insert a new record
- Raises `ValueError` if you try to create an entity that already has an ID
- After commit, the database assigns an ID and timestamps

**update() method:**
- **Validates** the entity has an ID (ensuring it exists)
- **Verifies** the entity exists in the database before updating
- Uses `session.merge()` instead of `session.add()`
- Raises `ValueError` if the entity is missing or doesn't exist
- Handles both attached and detached entities correctly

**Why merge() instead of add() for updates?**

SQLAlchemy's `merge()` is specifically designed for updates. It:
- Copies the state from your entity to the session-tracked instance
- Works correctly with detached entities (entities loaded in a previous session)
- Prevents issues when updating entities that aren't currently tracked

**Example of the difference:**

```python
# ❌ This will raise ValueError
new_model = Model(id=999, name="test")  # Already has an ID
await repo.create(new_model)  # Error: "Cannot create entity that already has an ID"

# ✅ Correct: create without ID
new_model = Model(name="test")
created = await repo.create(new_model)  # Works! Database assigns ID

# ✅ Correct: update existing entity
existing = await repo.get_by_id(1)
existing.name = "Updated"
updated = await repo.update(existing)  # Works!

# ❌ This will raise ValueError
non_existent = Model(id=99999, name="test")
await repo.update(non_existent)  # Error: "not found in database"
```

This validation ensures you can't accidentally:
- Insert a duplicate by using `create()` with an existing ID
- Try to update something that doesn't exist
- Mix up create and update operations

### 1. Generic Repository with TypeVar

```python
ModelType = TypeVar("ModelType", bound=SQLModel)

class BaseRepository(Generic[ModelType]):
    def __init__(self, model: type[ModelType], session: AsyncSession):
        self.model = model
```

**Why this is powerful:**

- Works with any SQLModel table class
- Type checkers (like mypy, Pylance) know what type you're working with
- You get autocomplete for model fields in your editor
- Catches type errors at development time, not runtime

### 2. Async All the Way

```python
async def get_by_id(self, id: int) -> ModelType | None:
    return await self.session.get(self.model, id)
```

**Why async matters:**

- Database I/O is slow (network latency, disk reads)
- Async lets other code run while waiting for the database
- Essential for high-performance web applications
- FastAPI is built for async—we match its paradigm

### 3. SQLModel's select() Function

```python
statement = select(self.model).offset(skip).limit(limit)
result = await self.session.exec(statement)
return result.all()
```

**This is SQLAlchemy 2.0 style:**

- Build query statements declaratively
- Type-safe (editor knows what columns exist)
- More Pythonic than string SQL
- Prevents SQL injection automatically

### 4. Session Management

Notice we don't create or close the session—we **receive it as a dependency**. This is crucial:

- Caller controls session lifecycle
- Enables transactions across multiple repository calls
- Follows Dependency Injection pattern
- FastAPI will provide the session automatically

**🎯 Checkpoint:** The `BaseRepository` provides the foundation. Now let's build domain-specific repositories on top of it.

---

## Step 2: Creating Domain-Specific Repositories

Now we'll create repositories for each entity, adding methods specific to their domain.

### Create the Model Repository

Create `backend/app/db/repositories/model_repository.py`:

```python
"""
Repository for AI Model entity

Provides database operations for the Model table with domain-specific queries.
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

    async def search(self, query: str, skip: int = 0, limit: int = 100) -> Sequence[Model]:
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
        # Use ilike for case-insensitive search (PostgreSQL specific)
        search_pattern = f"%{query}%"
        statement = (
            select(Model)
            .where(
                or_(
                    Model.name.ilike(search_pattern),
                    Model.display_name.ilike(search_pattern),
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

        # Exclude specific ID if provided (useful for updates)
        if exclude_id is not None:
            statement = statement.where(Model.id != exclude_id)

        result = await self.session.exec(statement)
        return result.first() is not None
```

**Key patterns in ModelRepository:**

### 1. Domain-Specific Queries

```python
async def get_by_name(self, name: str) -> Model | None:
    statement = select(Model).where(Model.name == name)
```

This method encapsulates the "get model by name" use case. The caller doesn't need to know about SQL or SQLModel syntax.

### 2. Flexible Search with OR

```python
statement = select(Model).where(
    or_(
        Model.name.ilike(search_pattern),
        Model.display_name.ilike(search_pattern),
        Model.organization.ilike(search_pattern),
    )
)
```

**What's happening:**

- `ilike()` is case-insensitive LIKE (PostgreSQL)
- `or_()` combines conditions with SQL OR
- `%query%` is the wildcard pattern (matches anywhere in string)

### 3. Validation Helpers

```python
async def name_exists(self, name: str, exclude_id: int | None = None) -> bool:
```

This method helps prevent duplicate names. The `exclude_id` parameter handles the update case elegantly—when updating model #5, we want to allow keeping its current name, but not taking another model's name.

### Create the Benchmark Repository

Create `backend/app/db/repositories/benchmark_repository.py`:

```python
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
```

### Create the BenchmarkResult Repository

Create `backend/app/db/repositories/benchmark_result_repository.py`:

```python
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
            .options(selectinload(BenchmarkResult.benchmark))  # Eager load benchmark
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
```

**Key pattern: Eager Loading with selectinload**

```python
.options(selectinload(BenchmarkResult.benchmark))
```

**Why this matters:**

Without eager loading:

```python
results = await repo.get_by_model_id(1)
for result in results:
    print(result.benchmark.name)  # ⚠️ Triggers a separate query for EACH result!
```

This is the **N+1 query problem**: 1 query for results, then N queries for benchmarks.

With eager loading:

```python
# Only 2 queries total: 1 for results, 1 for all their benchmarks
.options(selectinload(BenchmarkResult.benchmark))
```

**SQLAlchemy async note:** In async contexts, you must explicitly load relationships using `selectinload()` or `joinedload()`. Lazy loading doesn't work with async sessions.

### Create Repositories Package

Create `backend/app/db/repositories/__init__.py`:

```python
"""
Repositories package

Exports all repository classes for easy importing.
"""

from .model_repository import ModelRepository
from .benchmark_repository import BenchmarkRepository
from .benchmark_result_repository import BenchmarkResultRepository

__all__ = [
    "ModelRepository",
    "BenchmarkRepository",
    "BenchmarkResultRepository",
]
```

Update `backend/app/db/__init__.py`:

```python
"""
Database utilities package
"""

from .session import get_db, AsyncSessionLocal, engine, init_db
from .repository import BaseRepository
from .repositories import (
    ModelRepository,
    BenchmarkRepository,
    BenchmarkResultRepository,
)

__all__ = [
    "get_db",
    "AsyncSessionLocal",
    "engine",
    "init_db",
    "BaseRepository",
    "ModelRepository",
    "BenchmarkRepository",
    "BenchmarkResultRepository",
]
```

**🎯 Checkpoint:** You now have repositories for the three main entities. Let's test them!

---

## Step 3: Writing Repository Tests

Testing repositories is crucial—they're the foundation of your data layer. Let's write comprehensive tests.

### Update Test Fixtures

First, add a sample model fixture to `backend/tests/conftest.py`:

```python
@pytest.fixture
def sample_model():
    """
    Sample AI model for testing

    Returns a Model instance (not yet persisted to database)
    """
    from app.models.models import Model
    from datetime import date

    return Model(
        name="gpt-test",
        display_name="GPT Test Model",
        organization="Test Org",
        release_date=date(2024, 1, 1),
        description="A test model for unit tests",
        license="MIT",
        metadata_={"context_window": 8192, "pricing": "free"},
    )


@pytest.fixture
def sample_benchmark():
    """Sample benchmark for testing"""
    from app.models.models import Benchmark

    return Benchmark(
        name="TEST_BENCH",
        category="Testing",
        description="A benchmark for testing purposes",
        url="https://example.com/test-bench",
    )
```

Make sure you also have the `test_engine` and `test_session` fixtures from Module 1.1:

```python
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import event
import pytest

from app.config import settings


@pytest.fixture()
async def test_engine():
    """
    Create a fresh async engine for each test function
    This prevents event loop conflicts between tests
    """
    engine = create_async_engine(
        settings.database_url_async,
        echo=False,
        future=True,
    )
    yield engine
    await engine.dispose()


@pytest.fixture(scope="function")
async def test_session(test_engine):
    """
    One DB connection + outer transaction per test, always rolled back.
    Nested transaction (SAVEPOINT) allows code under test to call commit().
    """
    async with test_engine.connect() as conn:
        outer_tx = await conn.begin()

        # Build the session to this connection
        async_session_maker = async_sessionmaker(
            bind=conn,
            class_=AsyncSession,
            expire_on_commit=False,
        )

        async with async_session_maker() as session:
            # Start SAVEPOINT
            await session.begin_nested()

            # If the code under test calls commit(), the SAVEPOINT ends.
            # This listener recreates it so the session can keep working.
            @event.listens_for(session.sync_session, "after_transaction_end")
            def _restart_savepoint(sess, trans):
                if trans.nested and not trans._parent.nested:
                    sess.begin_nested()

            try:
                yield session
            finally:
                # Close session and rollback everything done in the test
                await session.close()
                # Only rollback if the transaction is still active
                if outer_tx.is_active:
                    await outer_tx.rollback()
```

### Create Repository Tests

Create `backend/tests/test_repositories.py`:

```python
"""
Tests for Repository Pattern Implementation

Tests all repository classes to ensure CRUD operations work correctly.
"""

import pytest
from datetime import date

from app.db.repositories import (
    ModelRepository,
    BenchmarkRepository,
    BenchmarkResultRepository,
)
from app.models.models import Model, Benchmark, BenchmarkResult


# =============================================================================
# ModelRepository Tests
# =============================================================================


async def test_model_repository_create(test_session, sample_model):
    """Test creating a model through the repository"""
    repo = ModelRepository(test_session)

    created = await repo.create(sample_model)

    assert created.id is not None
    assert created.name == "gpt-test"
    assert created.organization == "Test Org"
    assert created.created_at is not None


async def test_model_repository_get_by_id(test_session, sample_model):
    """Test retrieving a model by ID"""
    repo = ModelRepository(test_session)

    # Create first
    created = await repo.create(sample_model)

    # Retrieve
    retrieved = await repo.get_by_id(created.id)

    assert retrieved is not None
    assert retrieved.id == created.id
    assert retrieved.name == created.name


async def test_model_repository_get_by_id_not_found(test_session):
    """Test that get_by_id returns None for non-existent ID"""
    repo = ModelRepository(test_session)

    result = await repo.get_by_id(99999)

    assert result is None


async def test_model_repository_get_by_name(test_session, sample_model):
    """Test retrieving a model by unique name"""
    repo = ModelRepository(test_session)

    await repo.create(sample_model)

    retrieved = await repo.get_by_name("gpt-test")

    assert retrieved is not None
    assert retrieved.name == "gpt-test"
    assert retrieved.organization == "Test Org"


async def test_model_repository_get_all(test_session):
    """Test retrieving all models with pagination"""
    repo = ModelRepository(test_session)

    # Create multiple models
    for i in range(5):
        model = Model(
            name=f"model-{i}",
            display_name=f"Model {i}",
            organization="Test Org",
        )
        await repo.create(model)

    # Get first 3
    results = await repo.get_all(skip=0, limit=3)
    assert len(results) == 3

    # Get next 2
    results = await repo.get_all(skip=3, limit=3)
    assert len(results) == 2


async def test_model_repository_update(test_session, sample_model):
    """Test updating a model"""
    repo = ModelRepository(test_session)

    created = await repo.create(sample_model)
    original_id = created.id

    # Modify
    created.display_name = "Updated Name"
    created.organization = "New Org"

    # Update
    updated = await repo.update(created)

    assert updated.id == original_id
    assert updated.display_name == "Updated Name"
    assert updated.organization == "New Org"


async def test_model_repository_delete(test_session, sample_model):
    """Test deleting a model"""
    repo = ModelRepository(test_session)

    created = await repo.create(sample_model)
    model_id = created.id

    # Delete
    deleted = await repo.delete(model_id)
    assert deleted is True

    # Verify it's gone
    retrieved = await repo.get_by_id(model_id)
    assert retrieved is None


async def test_model_repository_delete_not_found(test_session):
    """Test that deleting non-existent model returns False"""
    repo = ModelRepository(test_session)

    deleted = await repo.delete(99999)
    assert deleted is False


async def test_model_repository_exists(test_session, sample_model):
    """Test checking if a model exists"""
    repo = ModelRepository(test_session)

    created = await repo.create(sample_model)

    assert await repo.exists(created.id) is True
    assert await repo.exists(99999) is False


async def test_model_repository_count(test_session):
    """Test counting total models"""
    repo = ModelRepository(test_session)

    # Initially empty (or has whatever is in test DB)
    initial_count = await repo.count()

    # Add 3 models
    for i in range(3):
        model = Model(
            name=f"count-test-{i}",
            display_name=f"Count Test {i}",
            organization="Test Org",
        )
        await repo.create(model)

    # Count should increase by 3
    new_count = await repo.count()
    assert new_count == initial_count + 3


async def test_model_repository_search(test_session):
    """Test searching models by name or organization"""
    repo = ModelRepository(test_session)

    # Create models with various names
    models = [
        Model(name="gpt-4", display_name="GPT-4", organization="OpenAI"),
        Model(name="gpt-3.5", display_name="GPT-3.5", organization="OpenAI"),
        Model(name="claude-3", display_name="Claude 3", organization="Anthropic"),
    ]

    for model in models:
        await repo.create(model)

    # Search for "gpt" should return 2
    results = await repo.search("gpt")
    assert len(results) == 2

    # Search for "OpenAI" should return 2
    results = await repo.search("OpenAI")
    assert len(results) == 2

    # Search for "anthropic" (case-insensitive) should return 1
    results = await repo.search("anthropic")
    assert len(results) == 1


async def test_model_repository_get_by_organization(test_session):
    """Test getting models filtered by organization"""
    repo = ModelRepository(test_session)

    # Create models from different orgs
    openai_model = Model(
        name="gpt-4", display_name="GPT-4", organization="OpenAI", release_date=date(2023, 3, 14)
    )
    anthropic_model = Model(
        name="claude-3",
        display_name="Claude 3",
        organization="Anthropic",
        release_date=date(2024, 3, 4),
    )

    await repo.create(openai_model)
    await repo.create(anthropic_model)

    # Get OpenAI models
    results = await repo.get_by_organization("OpenAI")
    assert len(results) == 1
    assert results[0].name == "gpt-4"


async def test_model_repository_name_exists(test_session, sample_model):
    """Test checking if a model name already exists"""
    repo = ModelRepository(test_session)

    await repo.create(sample_model)

    # Name exists
    assert await repo.name_exists("gpt-test") is True

    # Name doesn't exist
    assert await repo.name_exists("non-existent-model") is False


async def test_model_repository_name_exists_exclude_id(test_session):
    """Test name_exists with exclude_id for updates"""
    repo = ModelRepository(test_session)

    model = Model(name="original-name", display_name="Original", organization="Test Org")
    created = await repo.create(model)

    # Same name, excluding own ID -> should return False (name is available for this model)
    assert await repo.name_exists("original-name", exclude_id=created.id) is False

    # Create another model
    other_model = Model(name="other-name", display_name="Other", organization="Test Org")
    await repo.create(other_model)

    # Try to take other model's name -> should return True (conflict)
    assert await repo.name_exists("other-name", exclude_id=created.id) is True


# =============================================================================
# BenchmarkRepository Tests
# =============================================================================


async def test_benchmark_repository_create(test_session, sample_benchmark):
    """Test creating a benchmark"""
    repo = BenchmarkRepository(test_session)

    created = await repo.create(sample_benchmark)

    assert created.id is not None
    assert created.name == "TEST_BENCH"
    assert created.category == "Testing"


async def test_benchmark_repository_get_by_name(test_session, sample_benchmark):
    """Test getting benchmark by name"""
    repo = BenchmarkRepository(test_session)

    await repo.create(sample_benchmark)

    retrieved = await repo.get_by_name("TEST_BENCH")

    assert retrieved is not None
    assert retrieved.name == "TEST_BENCH"


async def test_benchmark_repository_get_by_category(test_session):
    """Test getting benchmarks by category"""
    repo = BenchmarkRepository(test_session)

    # Create benchmarks in different categories
    benchmarks = [
        Benchmark(name="MMLU", category="Knowledge", description="Knowledge test"),
        Benchmark(name="HumanEval", category="Coding", description="Code generation"),
        Benchmark(name="MATH", category="Math", description="Math problems"),
        Benchmark(name="GSM8K", category="Math", description="Grade school math"),
    ]

    for bench in benchmarks:
        await repo.create(bench)

    # Get math benchmarks
    results = await repo.get_by_category("Math")
    assert len(results) == 2
    assert all(b.category == "Math" for b in results)


async def test_benchmark_repository_get_all_categories(test_session):
    """Test getting unique list of categories"""
    repo = BenchmarkRepository(test_session)

    # Create benchmarks in various categories
    benchmarks = [
        Benchmark(name="B1", category="Knowledge"),
        Benchmark(name="B2", category="Coding"),
        Benchmark(name="B3", category="Knowledge"),  # Duplicate category
        Benchmark(name="B4", category="Math"),
    ]

    for bench in benchmarks:
        await repo.create(bench)

    categories = await repo.get_all_categories()

    # Should have 3 unique categories
    assert len(set(categories)) == 3
    assert "Knowledge" in categories
    assert "Coding" in categories
    assert "Math" in categories


# =============================================================================
# BenchmarkResultRepository Tests
# =============================================================================


async def test_benchmark_result_repository_create(test_session, sample_model, sample_benchmark):
    """Test creating a benchmark result"""
    model_repo = ModelRepository(test_session)
    benchmark_repo = BenchmarkRepository(test_session)
    result_repo = BenchmarkResultRepository(test_session)

    # Create model and benchmark first
    model = await model_repo.create(sample_model)
    benchmark = await benchmark_repo.create(sample_benchmark)

    # Create result
    result = BenchmarkResult(
        model_id=model.id,
        benchmark_id=benchmark.id,
        score=85.5,
        date_tested=date(2024, 1, 15),
        source="Test Suite",
    )

    created = await result_repo.create(result)

    assert created.id is not None
    assert created.score == 85.5
    assert created.model_id == model.id
    assert created.benchmark_id == benchmark.id


async def test_benchmark_result_repository_get_by_model_id(
    test_session, sample_model, sample_benchmark
):
    """Test getting all results for a model"""
    model_repo = ModelRepository(test_session)
    benchmark_repo = BenchmarkRepository(test_session)
    result_repo = BenchmarkResultRepository(test_session)

    model = await model_repo.create(sample_model)

    # Create multiple benchmarks
    bench1 = await benchmark_repo.create(sample_benchmark)
    bench2 = await benchmark_repo.create(
        Benchmark(name="BENCH2", category="Testing", description="Second test benchmark")
    )

    # Create results for same model
    await result_repo.create(
        BenchmarkResult(model_id=model.id, benchmark_id=bench1.id, score=80.0)
    )
    await result_repo.create(
        BenchmarkResult(model_id=model.id, benchmark_id=bench2.id, score=90.0)
    )

    # Get all results for this model
    results = await result_repo.get_by_model_id(model.id)

    assert len(results) == 2
    assert all(r.model_id == model.id for r in results)


async def test_benchmark_result_repository_get_by_benchmark_id(
    test_session, sample_benchmark
):
    """Test getting all results for a benchmark (across models)"""
    model_repo = ModelRepository(test_session)
    benchmark_repo = BenchmarkRepository(test_session)
    result_repo = BenchmarkResultRepository(test_session)

    benchmark = await benchmark_repo.create(sample_benchmark)

    # Create multiple models
    model1 = await model_repo.create(
        Model(name="model-1", display_name="Model 1", organization="Test")
    )
    model2 = await model_repo.create(
        Model(name="model-2", display_name="Model 2", organization="Test")
    )

    # Create results for same benchmark
    await result_repo.create(
        BenchmarkResult(model_id=model1.id, benchmark_id=benchmark.id, score=75.0)
    )
    await result_repo.create(
        BenchmarkResult(model_id=model2.id, benchmark_id=benchmark.id, score=85.0)
    )

    # Get all results for this benchmark
    results = await result_repo.get_by_benchmark_id(benchmark.id)

    assert len(results) == 2
    assert all(r.benchmark_id == benchmark.id for r in results)
    # Should be ordered by score descending
    assert results[0].score >= results[1].score


async def test_benchmark_result_repository_get_by_model_and_benchmark(
    test_session, sample_model, sample_benchmark
):
    """Test getting results for specific model-benchmark pair"""
    model_repo = ModelRepository(test_session)
    benchmark_repo = BenchmarkRepository(test_session)
    result_repo = BenchmarkResultRepository(test_session)

    model = await model_repo.create(sample_model)
    benchmark = await benchmark_repo.create(sample_benchmark)

    # Create multiple results for same model+benchmark (different dates)
    await result_repo.create(
        BenchmarkResult(
            model_id=model.id,
            benchmark_id=benchmark.id,
            score=80.0,
            date_tested=date(2024, 1, 1),
        )
    )
    await result_repo.create(
        BenchmarkResult(
            model_id=model.id,
            benchmark_id=benchmark.id,
            score=85.0,
            date_tested=date(2024, 2, 1),
        )
    )

    # Get results for this pair
    results = await result_repo.get_by_model_and_benchmark(model.id, benchmark.id)

    assert len(results) == 2
    assert all(r.model_id == model.id and r.benchmark_id == benchmark.id for r in results)


async def test_benchmark_result_repository_result_exists(
    test_session, sample_model, sample_benchmark
):
    """Test checking if a result already exists"""
    model_repo = ModelRepository(test_session)
    benchmark_repo = BenchmarkRepository(test_session)
    result_repo = BenchmarkResultRepository(test_session)

    model = await model_repo.create(sample_model)
    benchmark = await benchmark_repo.create(sample_benchmark)

    test_date = date(2024, 1, 15)

    # Initially doesn't exist
    assert (
        await result_repo.result_exists(model.id, benchmark.id, test_date)
    ) is False

    # Create result
    await result_repo.create(
        BenchmarkResult(
            model_id=model.id,
            benchmark_id=benchmark.id,
            score=80.0,
            date_tested=test_date,
        )
    )

    # Now it exists
    assert (
        await result_repo.result_exists(model.id, benchmark.id, test_date)
    ) is True

    # Different date doesn't exist
    assert (
        await result_repo.result_exists(model.id, benchmark.id, date(2024, 2, 1))
    ) is False
```

### Run the Repository Tests

```bash
cd backend
uv run pytest tests/test_repositories.py -v
cd ..
```

You should see all tests passing! 🎉

```
tests/test_repositories.py::test_model_repository_create PASSED
tests/test_repositories.py::test_model_repository_get_by_id PASSED
tests/test_repositories.py::test_model_repository_get_by_id_not_found PASSED
... (26 more tests)
====== 29 passed in X.XX s ======
```

**What do these tests verify?**

- ✅ CRUD operations work correctly
- ✅ Pagination and filtering work
- ✅ Domain-specific queries return expected results
- ✅ Validation helpers work (name_exists, result_exists)
- ✅ Relationships are properly loaded
- ✅ Edge cases are handled (not found, duplicates)

**🎯 Checkpoint:** Your repository layer is fully tested and working!

---

## Step 4: Using Repositories in FastAPI (Preview)

Let's see how repositories will be used in FastAPI endpoints (we'll build these fully in Module 2.x).

### Dependency Injection Pattern

FastAPI's dependency injection system will provide database sessions to our endpoints:

```python
from fastapi import Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db import get_db, ModelRepository
from app.models.models import ModelResponse


@app.get("/api/v1/models/{id}", response_model=ModelResponse)
async def get_model(
    id: int,
    session: AsyncSession = Depends(get_db)  # FastAPI injects the session
):
    """Get a single model by ID"""
    repo = ModelRepository(session)

    model = await repo.get_by_id(id)

    if not model:
        raise HTTPException(status_code=404, detail="Model not found")

    return model
```

**What's happening here:**

1. `Depends(get_db)` tells FastAPI to call `get_db()` and pass the result to `session`
2. `get_db()` is an async generator that yields a database session
3. FastAPI automatically closes the session when the request completes
4. We create a repository instance with the session
5. We use the repository to fetch data
6. SQLModel automatically validates the response matches `ModelResponse`

**Benefits of this pattern:**

- **Testable**: Mock the repository in tests, not the database
- **Clean separation**: Endpoint focuses on HTTP, repository handles data
- **Reusable**: Same repository logic used across multiple endpoints
- **Type-safe**: Editor knows what `model` is and what fields it has

### Example with Business Logic (Service Layer Preview)

In Module 2.x, we'll add a service layer between endpoints and repositories:

```python
from app.services.model_service import ModelService


@app.post("/api/v1/models", response_model=ModelResponse, status_code=201)
async def create_model(
    model_data: ModelCreate,
    session: AsyncSession = Depends(get_db)
):
    """Create a new AI model"""
    service = ModelService(session)

    # Service handles validation, business rules, and orchestration
    created_model = await service.create_model(model_data)

    return created_model
```

The service might look like:

```python
class ModelService:
    def __init__(self, session: AsyncSession):
        self.model_repo = ModelRepository(session)

    async def create_model(self, model_data: ModelCreate) -> Model:
        # Business rule: Check for duplicate names
        if await self.model_repo.name_exists(model_data.name):
            raise ValueError(f"Model '{model_data.name}' already exists")

        # Business rule: Validate organization
        if model_data.organization not in ALLOWED_ORGANIZATIONS:
            raise ValueError(f"Unknown organization: {model_data.organization}")

        # Create the model
        model = Model(**model_data.model_dump())
        return await self.model_repo.create(model)
```

**The architecture emerges:**

```
Endpoint → Service → Repository → Database
  HTTP      Logic      Data       Storage
```

Each layer has a clear responsibility and can be tested independently.

**🎯 Checkpoint:** You understand how repositories fit into the larger application architecture.

---

## Understanding Async Session Management

Let's dive deeper into how async sessions work and why we manage them the way we do.

### The Session Lifecycle

A database session represents a "workspace" for database operations:

1. **Create session** - Get a connection from the pool
2. **Execute queries** - Run SELECT, INSERT, UPDATE, DELETE
3. **Commit/Rollback** - Make changes permanent or discard them
4. **Close session** - Return connection to pool

### Our Session Management Pattern

In `backend/app/db/session.py`, we defined:

```python
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for FastAPI routes"""
    async with AsyncSessionLocal() as session:
        yield session
```

**Why async with?**

The `async with` statement:

- Creates the session
- Yields it to the caller
- Automatically closes it when done (even if an exception occurs)

This is the **context manager pattern**—it guarantees cleanup.

### Transaction Behavior

By default, sessions auto-commit in SQLAlchemy 2.0:

```python
# Each operation commits immediately
await session.add(model)
await session.commit()  # Explicit commit
```

For **multi-operation transactions**, use `begin()`:

```python
async with session.begin():
    # Multiple operations in one transaction
    model = await model_repo.create(model_data)
    result = await result_repo.create(result_data)
    # If any operation fails, all are rolled back
```

### Testing Pattern: Nested Transactions

Our test fixtures use a clever pattern to isolate tests:

```python
async with test_engine.connect() as conn:
    outer_tx = await conn.begin()  # Outer transaction

    async with async_session_maker() as session:
        await session.begin_nested()  # SAVEPOINT

        # Test code runs here
        # Can call commit(), but it only commits the SAVEPOINT

        # After test finishes...
        await outer_tx.rollback()  # Rollback everything
```

**Why this works:**

- Each test gets a real session that can commit
- All changes are inside a SAVEPOINT
- After the test, we rollback the outer transaction
- Database returns to clean state for next test

This gives us **test isolation** without recreating the database.

**🎯 Checkpoint:** You understand how sessions are managed in both production and testing.

---

## Key Design Patterns Explained

Let's reflect on the patterns we've implemented and why they matter.

### Pattern 1: Generic Base Repository

**Problem:** Every entity needs the same CRUD operations.

**Solution:** Use Python generics to create a reusable base class.

**Benefits:**

- Write CRUD logic once, reuse everywhere
- Type safety through generics
- Consistency across all repositories
- Easy to add global features (e.g., soft deletes, audit logging)

**When to use:**

- You have multiple entities with similar operations
- You want type-safe abstractions
- You value DRY (Don't Repeat Yourself)

### Pattern 2: Domain-Specific Repositories

**Problem:** Each entity has unique query requirements.

**Solution:** Inherit from base and add specialized methods.

**Benefits:**

- Encapsulates domain knowledge
- Expressive, readable code (e.g., `repo.get_by_name()` is clear)
- Easy to optimize specific queries
- Testable business logic

**When to use:**

- Entities have unique querying patterns
- You want to hide SQL/ORM complexity
- You need to enforce business rules at the data layer

### Pattern 3: Dependency Injection

**Problem:** How do endpoints get repository instances?

**Solution:** FastAPI's `Depends()` injects dependencies automatically.

**Benefits:**

- Loose coupling (endpoints don't create repositories)
- Easy to swap implementations (e.g., for testing)
- Clear dependencies (visible in function signature)
- Framework manages lifecycle

**When to use:**

- Building web applications with FastAPI
- You want testable code
- You need to manage shared resources (like database sessions)

### Pattern 4: Eager Loading with selectinload

**Problem:** N+1 query problem degrades performance.

**Solution:** Use SQLAlchemy's `selectinload()` to load relationships upfront.

**Benefits:**

- Predictable query count (2 queries instead of N+1)
- Better performance at scale
- Works in async contexts

**When to use:**

- You're loading collections with relationships
- You know you'll access the related data
- You're using async SQLAlchemy

**Trade-off:** Eager loading fetches more data upfront, which may be wasteful if you don't always need the relationships. Use `selectinload()` when you know you'll need the data, and lazy load when it's optional.

---

## Common Pitfalls and How to Avoid Them

### Pitfall 1: Forgetting async/await

**Symptom:**

```python
# ❌ Forgot await
model = repo.get_by_id(1)  # Returns a coroutine, not a Model!
print(model.name)  # AttributeError: coroutine has no attribute 'name'
```

**Solution:**

```python
# ✅ Use await
model = await repo.get_by_id(1)
print(model.name)
```

**Rule:** Every repository method is async. Always use `await`.

### Pitfall 2: Session Closed Too Early

**Symptom:**

```python
async def get_model_with_results(id: int):
    async with AsyncSessionLocal() as session:
        repo = ModelRepository(session)
        model = await repo.get_by_id(id)
    # Session is closed here!

    # ❌ Trying to access relationship outside session
    return model.benchmark_results  # Error: detached instance
```

**Solution:**

```python
async def get_model_with_results(id: int):
    async with AsyncSessionLocal() as session:
        repo = ModelRepository(session)

        # Eagerly load relationships before session closes
        statement = select(Model).where(Model.id == id).options(
            selectinload(Model.benchmark_results)
        )
        result = await session.exec(statement)
        model = result.first()

        return model  # Safe to access relationships now
```

**Rule:** Load all needed data (including relationships) while the session is open.

### Pitfall 3: Trying to Create with an ID or Update Without Verification

**Symptom:**

```python
# ❌ Trying to create an entity that already has an ID
model = Model(id=5, name="test")
await repo.create(model)  # ValueError: Cannot create entity that already has an ID

# ❌ Trying to update an entity that doesn't exist
fake_model = Model(id=99999, name="test")
await repo.update(fake_model)  # ValueError: not found in database
```

**Solution:**

Our repository methods now include validation to catch these mistakes early with clear error messages.

```python
# ✅ Create new entities without IDs
new_model = Model(name="test")
created = await repo.create(new_model)  # ID assigned by database

# ✅ Update existing entities
existing = await repo.get_by_id(1)
if existing:
    existing.name = "Updated"
    await repo.update(existing)
```

**Why this matters:**
- Catches mistakes at the repository layer with clear messages
- Prevents confusing database errors
- Makes intent explicit (creating vs updating)
- Ensures consistency across your application

### Pitfall 4: Not Using Type Hints

**Symptom:**

```python
# ❌ No type hints - editor can't help
async def get_by_id(self, id):
    return await self.session.get(self.model, id)
```

**Solution:**

```python
# ✅ Full type hints
async def get_by_id(self, id: int) -> ModelType | None:
    return await self.session.get(self.model, id)
```

**Benefits:**

- Editor autocomplete works
- Type checker catches errors
- Code is self-documenting

**Rule:** Always add type hints to repository methods.

---

## What You've Accomplished

Congratulations! 🎉 You've implemented a professional repository layer. Here's what you now have:

1. **Solid Architectural Foundation**

   - Three-layer architecture (API → Service → Repository)
   - Clean separation of concerns
   - SOLID principles in practice

2. **Reusable Base Repository**

   - Generic async CRUD operations
   - Type-safe with Python generics
   - Works with any SQLModel table

3. **Domain-Specific Repositories**

   - `ModelRepository` with search, filtering, validation
   - `BenchmarkRepository` with category queries
   - `BenchmarkResultRepository` with relationship loading

4. **Comprehensive Test Suite**

   - 29 tests covering all operations
   - Test isolation with nested transactions
   - Edge cases handled

5. **Async Mastery**

   - Proper session management
   - Context managers for cleanup
   - Understanding of async database patterns

6. **Production-Ready Patterns**
   - Dependency injection ready for FastAPI
   - Eager loading to prevent N+1 queries
   - Validation helpers for business rules

### Key Takeaways

- **Repository Pattern abstracts data access** - your application doesn't know about SQL
- **Generic base classes reduce duplication** - write once, use everywhere
- **Async is essential for performance** - don't block on I/O
- **Type hints make code safer and clearer** - let tools help you
- **Tests give confidence** - refactor without fear
- **Separation of concerns scales** - each layer has one job
- **Eager loading prevents performance issues** - be deliberate about relationships

---

## What's Next?

In **Module 2.1: Pydantic Schemas & API Foundation**, you'll:

- Build FastAPI endpoints using your repositories
- Learn request/response schema design with SQLModel
- Implement proper error handling and status codes
- Add API documentation with OpenAPI
- Use dependency injection to connect everything
- Create integration tests for the API layer

You've built the data layer. Now it's time to expose it through a beautiful REST API!

---

## Hands-On Exercise

Before moving to the next module, try these challenges:

### Exercise 1: Create Opinion and UseCase Repositories

Following the patterns you've learned, implement:

- `OpinionRepository` with methods:
  - `get_by_model_id(model_id: int)`
  - `get_by_sentiment(sentiment: str)`
  - `search_by_content(query: str)`
- `UseCaseRepository` with methods:
  - `get_by_model_id(model_id: int)`
  - `get_by_use_case(use_case: str)`

**Acceptance Criteria:**

- Inherit from `BaseRepository`
- Include docstrings explaining each method
- Write tests for all methods
- Use proper type hints

### Exercise 2: Add Soft Delete

Implement soft delete functionality in `BaseRepository`:

- Add an `is_deleted` field to models (requires migration)
- Modify `delete()` to set `is_deleted=True` instead of removing the row
- Modify `get_all()` to filter out deleted entities by default
- Add `get_all_including_deleted()` method

**Acceptance Criteria:**

- All existing tests still pass
- New tests verify soft delete behavior
- Can restore deleted entities

### Exercise 3: Add Caching

Add simple in-memory caching to `get_by_id()`:

- Use a dictionary to cache recently fetched entities
- Implement cache invalidation on `update()` and `delete()`
- Add a TTL (time-to-live) for cache entries

**Acceptance Criteria:**

- First `get_by_id(1)` hits database
- Second `get_by_id(1)` returns cached value
- After update, next `get_by_id(1)` fetches fresh data

---

## Additional Resources

### Repository Pattern

- [Martin Fowler on Repository Pattern](https://martinfowler.com/eaaCatalog/repository.html)
- [Repository Pattern in Python](https://www.cosmicpython.com/book/chapter_02_repository.html)

### SQLModel & SQLAlchemy

- [SQLModel Relationships](https://sqlmodel.tiangolo.com/tutorial/relationship-attributes/)
- [SQLAlchemy Async ORM](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [Eager Loading Strategies](https://docs.sqlalchemy.org/en/20/orm/queryguide/relationships.html#loading-strategies)

### Async Python

- [AsyncIO in Python](https://docs.python.org/3/library/asyncio.html)
- [Real Python: Async IO](https://realpython.com/async-io-python/)

### Testing

- [Pytest Async Guide](https://pytest-asyncio.readthedocs.io/)
- [Testing FastAPI with Databases](https://fastapi.tiangolo.com/tutorial/testing/)

---

**Next Module:** [Module 2.1 - Pydantic Schemas & API Foundation](./module-2.1-api-foundation.md)
