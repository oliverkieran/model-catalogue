# Module 2.1: SQLModel Schemas & API Foundation - Building a Professional REST API

**Duration:** 2 hours
**Difficulty:** Intermediate
**Prerequisites:** Module 1.1 (Database Design) and Module 1.2 (Repository Pattern) complete

---

## Introduction: From Data Layer to API Layer

You've built a solid foundation with your database models and repository layer. Now comes an exciting moment: exposing your data to the world through a REST API.

But here's a critical question: **Should you send your database models directly to API clients?**

```python
# ❌ Tempting but problematic
@app.get("/api/v1/models/{id}")
async def get_model(id: int):
    model = await repo.get_by_id(id)
    return model  # Sending database model directly!
```

**Why this is dangerous:**

- **Security risk**: Exposes internal database structure to the world
- **Coupling**: API changes force database changes and vice versa
- **No input validation**: Anyone can send anything to your endpoints
- **Password leakage**: If you add sensitive fields to models, they're automatically exposed
- **Breaking changes**: Renaming a database column breaks all API clients
- **No control**: Can't easily customize what fields appear in responses

**The solution: Request/Response Schemas**

Professional APIs use dedicated schema classes that define **contracts** between the API and clients:

```python
# ✅ Professional approach with schemas
@app.get("/api/v1/models/{id}", response_model=ModelResponse)
async def get_model(id: int):
    model = await repo.get_by_id(id)
    return model  # FastAPI automatically validates against ModelResponse
```

This simple addition gives you:

- **Type safety**: FastAPI validates responses match the schema
- **API documentation**: Automatic OpenAPI/Swagger docs
- **Flexibility**: API and database can evolve independently
- **Security**: Only explicitly defined fields are exposed
- **Clarity**: Clients know exactly what to expect

In this module, you'll learn to:

- **Understand SQLModel's unified approach** to reduce duplication between database and API schemas
- **Design request/response schemas** that make your API intuitive and safe
- **Build FastAPI routers** organized by domain with proper dependency injection
- **Generate automatic API documentation** that clients will love
- **Test your API** with FastAPI's TestClient
- **Apply REST conventions** that make your API predictable and professional

This module bridges the gap between your data layer and the outside world. Master this, and you'll be able to build production-grade APIs for any project.

---

## What You'll Build

By the end of this module, you'll have:

- ✅ Request/response schemas for all entities (Models, Benchmarks, BenchmarkResults)
- ✅ FastAPI routers organized by domain (`/api/v1/models`, `/api/v1/benchmarks`)
- ✅ Your first complete CRUD endpoint (read operations for models)
- ✅ Automatic OpenAPI documentation at `/docs`
- ✅ Dependency injection pattern for database sessions
- ✅ Comprehensive API tests with TestClient
- ✅ Understanding of REST API design principles
- ✅ Foundation for full CRUD operations in Module 2.2

---

## Understanding API Design Principles

Before we code, let's understand what makes a good API.

### The REST Philosophy

**REST (Representational State Transfer)** is a set of conventions that make APIs predictable:

```
Resource-oriented URLs:
  GET    /api/v1/models              # List all models
  POST   /api/v1/models              # Create a model
  GET    /api/v1/models/{id}         # Get one model
  PUT    /api/v1/models/{id}         # Update a model
  DELETE /api/v1/models/{id}         # Delete a model

Related resources:
  GET    /api/v1/models/{id}/benchmarks  # Get model's benchmark results

Filtering & pagination:
  GET    /api/v1/models?organization=OpenAI&limit=10
```

**Key principles:**

1. **Resources are nouns** (models, benchmarks), not verbs
2. **HTTP methods convey action** (GET retrieves, POST creates, PUT updates, DELETE removes)
3. **URLs form a hierarchy** that reflects relationships
4. **Status codes communicate outcome** (200 OK, 404 Not Found, 400 Bad Request)
5. **Responses are consistent** across all endpoints

### The Schema Layers in SQLModel

SQLModel's brilliance is **reducing duplication** through inheritance. Let's see the pattern:

```python
# Layer 1: Base Model (shared fields)
class ModelBase(SQLModel):
    name: str
    organization: str
    # Common fields used in multiple contexts

# Layer 2: Database Table (inherits base + adds DB-specific)
class Model(ModelBase, TimestampMixin, table=True):
    id: int | None = Field(default=None, primary_key=True)
    metadata_: dict | None = Field(...)
    # Relationships, constraints, indexes

# Layer 3: Request Schemas (inherit base)
class ModelCreate(ModelBase):
    """For POST requests - accepts all base fields"""
    metadata_: dict | None = None

class ModelUpdate(SQLModel):
    """For PUT/PATCH requests - all fields optional"""
    name: str | None = None
    organization: str | None = None
    # ...all fields optional for partial updates

# Layer 4: Response Schema (base + generated fields)
class ModelResponse(ModelBase):
    """For API responses - includes database-generated fields"""
    id: int
    metadata_: dict | None = None
    created_at: datetime
    updated_at: datetime
```

**Why this structure?**

- **ModelBase**: Define common fields once, reuse everywhere
- **Model**: The source of truth for database structure
- **ModelCreate**: What users send when creating (no id, no timestamps)
- **ModelUpdate**: What users send when updating (everything optional)
- **ModelResponse**: What API returns (includes id and timestamps)

**The win:** Change a field definition in `ModelBase`, and it propagates to all schemas automatically!

### HTTP Status Codes That Tell a Story

Professional APIs use status codes to communicate:

```python
200 OK              # Successful GET, PUT, DELETE
201 Created         # Successful POST (created new resource)
204 No Content      # Successful DELETE (no response body needed)
400 Bad Request     # Client sent invalid data
404 Not Found       # Resource doesn't exist
422 Unprocessable   # Validation failed (FastAPI's default)
500 Server Error    # Something broke on our end
```

FastAPI makes this easy:

```python
@app.post("/api/v1/models", response_model=ModelResponse, status_code=201)
async def create_model(...):
    # FastAPI automatically returns 201 Created
    return created_model

@app.get("/api/v1/models/{id}", response_model=ModelResponse)
async def get_model(id: int):
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    return model
```

**🎯 Checkpoint:** You understand that schemas create a contract between your API and clients, and that SQLModel reduces duplication through inheritance.

---

## Step 1: Understanding the Existing Schema Structure

Good news! In your `backend/app/models/models.py`, you **already have schemas defined** following SQLModel best practices. Let's examine what's already there:

```python
# From models.py - this pattern is already implemented!

class ModelBase(SQLModel):
    """Shared fields"""
    name: str = Field(max_length=255, index=True, unique=True)
    display_name: str = Field(max_length=255)
    organization: str = Field(max_length=255)
    release_date: date | None = Field(default=None)
    description: str | None = Field(default=None, sa_column=Column(Text))
    license: str | None = Field(default=None, max_length=255)

class Model(ModelBase, TimestampMixin, table=True):
    """Database table"""
    id: int | None = Field(default=None, primary_key=True)
    metadata_: dict | None = Field(...)
    # Relationships...

class ModelCreate(ModelBase):
    """For POST /api/v1/models"""
    metadata_: dict | None = None

class ModelUpdate(SQLModel):
    """For PUT /api/v1/models/{id}"""
    name: str | None = Field(default=None, max_length=255)
    # All fields optional...

class ModelResponse(ModelBase):
    """For responses"""
    id: int
    metadata_: dict | None = None
    created_at: datetime
    updated_at: datetime
```

**What makes this structure excellent:**

### 1. Clear Separation of Concerns

```python
ModelCreate   # What clients send when creating (input validation)
ModelUpdate   # What clients send when updating (partial updates)
ModelResponse # What API returns (includes generated fields)
Model         # What database stores (internal representation)
```

### 2. Type Safety Throughout

FastAPI validates:

- **Requests** against Create/Update schemas (rejects invalid data)
- **Responses** against Response schemas (catches programming errors)

### 3. Automatic API Documentation

FastAPI uses these schemas to generate OpenAPI docs showing:

- Required vs optional fields
- Field types and constraints
- Example request/response payloads

### 4. Evolution Without Breaking Changes

You can:

- Add fields to database without changing API
- Add optional API fields without database changes
- Version your API while keeping old schemas working

**The pattern repeats** for all entities:

```
BenchmarkBase → Benchmark, BenchmarkCreate, BenchmarkUpdate, BenchmarkResponse
BenchmarkResultBase → BenchmarkResult, BenchmarkResultCreate, etc.
OpinionBase → Opinion, OpinionCreate, OpinionUpdate, OpinionResponse
UseCaseBase → UseCase, UseCaseCreate, UseCaseUpdate, UseCaseResponse
```

**🎯 Checkpoint:** Your schemas are already defined and follow best practices! Now let's use them in FastAPI endpoints.

---

## Step 2: Creating the API Router Structure

FastAPI encourages organizing routes by domain using **APIRouter**. This keeps your code modular and testable.

### Understanding APIRouter

Instead of putting all routes in `main.py`:

```python
# ❌ Everything in main.py gets messy
@app.get("/api/v1/models")
async def list_models(): ...

@app.get("/api/v1/benchmarks")
async def list_benchmarks(): ...

@app.get("/api/v1/opinions")
async def list_opinions(): ...
# ... 30 more endpoints
```

We use routers to **organize by domain**:

```python
# ✅ Organized with routers
# In routers/models.py
router = APIRouter(prefix="/api/v1/models", tags=["models"])

@router.get("/")
async def list_models(): ...

@router.get("/{id}")
async def get_model(id: int): ...

# In main.py - just include the router
app.include_router(models_router)
```

**Benefits:**

- **Separation**: Each domain (models, benchmarks) in its own file
- **Testing**: Test routers independently
- **Reusability**: Same router can be included in multiple apps
- **Documentation**: Tags group endpoints in Swagger UI
- **Team work**: Different developers work on different routers

### Create the Router Directory Structure

Let's create the API router structure:

```bash
mkdir -p backend/app/api/v1
touch backend/app/api/__init__.py
touch backend/app/api/v1/__init__.py
touch backend/app/api/v1/models.py
touch backend/app/api/v1/benchmarks.py
```

**🎯 Checkpoint:** You understand that routers help organize endpoints by domain, making your codebase maintainable.

---

## Step 3: Building Your First Router - Models Endpoints

Let's build a complete router for the Models resource with proper patterns.

### Create the Models Router

Create `backend/app/api/v1/models.py`:

```python
"""
Models API Router

Provides REST endpoints for AI model management:
- List models with pagination
- Get individual model details
- Search models (coming in Module 2.2)
- Create/Update/Delete models (coming in Module 2.2)
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Sequence

from app.db import get_db
from app.db.repositories import ModelRepository
from app.models.models import ModelResponse

# Create router with prefix and tags
router = APIRouter(
    prefix="/api/v1/models",
    tags=["models"],
    responses={
        404: {"description": "Model not found"},
        422: {"description": "Validation error"},
    },
)


@router.get("/", response_model=list[ModelResponse])
async def list_models(
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=20, le=100, description="Maximum records to return"),
    session: AsyncSession = Depends(get_db),
) -> Sequence[ModelResponse]:
    """
    List all AI models with pagination.

    - **skip**: Number of records to skip (for pagination)
    - **limit**: Maximum number of records to return (max 100)

    Returns a list of AI models with their basic information.
    """
    repo = ModelRepository(session)
    models = await repo.get_all(skip=skip, limit=limit)
    return models


@router.get("/{model_id}", response_model=ModelResponse)
async def get_model(
    model_id: int,
    session: AsyncSession = Depends(get_db),
) -> ModelResponse:
    """
    Get a specific AI model by ID.

    - **model_id**: The unique identifier of the model

    Returns detailed information about the model including metadata.

    Raises:
        HTTPException 404: If model with given ID doesn't exist
    """
    repo = ModelRepository(session)
    model = await repo.get_by_id(model_id)

    if not model:
        raise HTTPException(
            status_code=404,
            detail=f"Model with id {model_id} not found"
        )

    return model


@router.get("/name/{model_name}", response_model=ModelResponse)
async def get_model_by_name(
    model_name: str,
    session: AsyncSession = Depends(get_db),
) -> ModelResponse:
    """
    Get a specific AI model by its unique name.

    - **model_name**: The unique name of the model (e.g., "gpt-4", "claude-3-opus")

    Returns detailed information about the model.

    Raises:
        HTTPException 404: If model with given name doesn't exist
    """
    repo = ModelRepository(session)
    model = await repo.get_by_name(model_name)

    if not model:
        raise HTTPException(
            status_code=404,
            detail=f"Model with name '{model_name}' not found"
        )

    return model
```

**Let's break down the key patterns:**

### 1. Router Configuration

```python
router = APIRouter(
    prefix="/api/v1/models",      # All routes start with this
    tags=["models"],               # Groups endpoints in API docs
    responses={...}                # Common error responses
)
```

**What this does:**

- `prefix`: Routes defined as `@router.get("/")` become `/api/v1/models/`
- `tags`: Swagger UI groups all "models" endpoints together
- `responses`: Documents common error cases for all endpoints

### 2. Dependency Injection for Database Sessions

```python
async def list_models(
    session: AsyncSession = Depends(get_db),  # FastAPI injects this!
):
    repo = ModelRepository(session)
```

**How it works:**

1. FastAPI sees `Depends(get_db)`
2. Calls `get_db()` which yields a database session
3. Injects the session into your function
4. After the request, closes the session automatically

**Benefits:**

- **No manual session management**: FastAPI handles lifecycle
- **Testable**: Mock `get_db` in tests
- **Clean code**: No try/finally blocks needed
- **Transaction control**: Session per request pattern

### 3. Query Parameters with Validation

```python
skip: int = Query(default=0, ge=0, description="Number of records to skip"),
limit: int = Query(default=20, le=100, description="Maximum records to return"),
```

**What `Query` does:**

- `default=0`: If not provided, uses 0
- `ge=0`: Greater than or equal to 0 (validation)
- `le=100`: Less than or equal to 100 (prevents massive queries)
- `description`: Shows in API documentation

**Validation happens automatically:**

```bash
GET /api/v1/models?skip=-5        # ❌ Returns 422: skip must be >= 0
GET /api/v1/models?limit=1000     # ❌ Returns 422: limit must be <= 100
GET /api/v1/models?skip=10&limit=20  # ✅ Works perfectly
```

### 4. Response Model Validation

```python
@router.get("/", response_model=list[ModelResponse])
async def list_models(...) -> Sequence[ModelResponse]:
```

**Two levels of type safety:**

1. **Function annotation** (`-> Sequence[ModelResponse]`): For your editor/type checker
2. **FastAPI's `response_model`**: For runtime validation and docs

**What happens:**

- Your repository returns `Sequence[Model]` (database models)
- FastAPI converts each `Model` to `ModelResponse` automatically
- If conversion fails, raises 500 error (catches programming bugs)
- API docs show exact response structure

### 5. Error Handling with HTTPException

```python
if not model:
    raise HTTPException(
        status_code=404,
        detail=f"Model with id {model_id} not found"
    )
```

**Why HTTPException:**

- FastAPI catches it and returns proper HTTP response
- Sets status code automatically
- Returns JSON: `{"detail": "Model with id 5 not found"}`
- Clean error responses for API clients

**🎯 Checkpoint:** You've built a complete router with proper dependency injection, validation, and error handling!

---

## Step 4: Creating the Benchmarks Router

Let's apply the same patterns to benchmarks. This reinforces the concepts and shows how consistent your API becomes.

Create `backend/app/api/v1/benchmarks.py`:

```python
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
            status_code=404,
            detail=f"Benchmark with id {benchmark_id} not found"
        )

    return benchmark
```

**New pattern: Conditional Queries**

```python
if category:
    benchmarks = await repo.get_by_category(category, skip=skip, limit=limit)
else:
    benchmarks = await repo.get_all(skip=skip, limit=limit)
```

This allows flexible querying:

```bash
GET /api/v1/benchmarks                    # All benchmarks
GET /api/v1/benchmarks?category=Coding    # Only coding benchmarks
GET /api/v1/benchmarks?category=Math&limit=5  # 5 math benchmarks
```

**Utility endpoint pattern:**

```python
@router.get("/categories", response_model=list[str])
async def list_categories(...):
```

Utility endpoints provide **metadata** that helps clients use your API:

- List of valid categories
- List of organizations
- Available tags
- Enum values

These make building frontends easier (populate dropdowns without hardcoding).

**🎯 Checkpoint:** You see how the same patterns apply across different resources, creating a consistent API.

---

## Step 5: Integrating Routers into the Main Application

Now let's wire everything together in `main.py`.

Update `backend/app/main.py`:

```python
"""
Model Catalogue API - Main Application Entry Point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import models, benchmarks

VERSION = "0.1.0"

# Create FastAPI app instance
app = FastAPI(
    title="Model Catalogue API",
    description=(
        "REST API for managing and comparing AI models. "
        "Track model performance on benchmarks, public opinions, and use cases."
    ),
    version=VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite's default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(models.router)
app.include_router(benchmarks.router)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Model Catalogue API",
        "status": "operational",
        "version": VERSION,
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/api/v1/health")
async def health_check():
    """
    Health check endpoint for monitoring.

    Returns service status and component health.
    """
    return {
        "status": "healthy",
        "version": VERSION,
        "components": {
            "database": "connected",
            "api": "operational",
        }
    }
```

**Key additions:**

### 1. Router Inclusion

```python
from app.api.v1 import models, benchmarks

app.include_router(models.router)
app.include_router(benchmarks.router)
```

This registers all routes from your routers. Now requests to `/api/v1/models/` route to your models router.

### 2. Enhanced API Metadata

```python
app = FastAPI(
    title="Model Catalogue API",
    description="...",
    version=VERSION,
    docs_url="/docs",      # Swagger UI
    redoc_url="/redoc",    # ReDoc alternative UI
)
```

This metadata appears in the automatically generated API documentation.

### 3. Informative Root Endpoint

```python
@app.get("/")
async def root():
    return {
        "docs": "/docs",
        "redoc": "/redoc",
    }
```

Guides developers to your API documentation.

**Create the router package init file** `backend/app/api/v1/__init__.py`:

```python
"""
API v1 - REST API version 1

Includes:
- Models endpoints: /api/v1/models
- Benchmarks endpoints: /api/v1/benchmarks
"""

from . import models, benchmarks

__all__ = ["models", "benchmarks"]
```

**🎯 Checkpoint:** Your API is now fully wired! Let's test it.

---

## Step 6: Testing the API Interactively

Let's start the development server and explore your API!

### Start the Development Server

```bash
cd backend
uv run uvicorn app.main:app --reload
```

You should see:

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Explore the Automatic Documentation

Open your browser to **http://localhost:8000/docs**

You'll see **Swagger UI** with:

- ✅ All endpoints organized by tags ("models", "benchmarks")
- ✅ Request/response schemas with example data
- ✅ "Try it out" buttons to test endpoints interactively
- ✅ Parameter descriptions and validation rules
- ✅ Response status codes and error formats

**Try it:**

1. Click on `GET /api/v1/models/`
2. Click "Try it out"
3. Set `limit` to 5
4. Click "Execute"
5. See the response (likely empty if you haven't created models yet)

**Alternative documentation:** Visit **http://localhost:8000/redoc** for ReDoc's cleaner, read-only documentation.

### Test with curl

```bash
# Health check
curl http://localhost:8000/api/v1/health

# List models
curl http://localhost:8000/api/v1/models/

# List benchmarks
curl http://localhost:8000/api/v1/benchmarks/

# Get categories
curl http://localhost:8000/api/v1/benchmarks/categories
```

### What You're Seeing

Your API is live! Even without data, you can:

- See proper JSON responses
- Observe error handling (try `GET /api/v1/models/999`)
- Validate query parameters (try `?limit=1000`)
- Explore the documentation

**🎯 Checkpoint:** Your API is running with automatic, interactive documentation!

---

## Step 7: Writing API Tests - The Smart Way

You've already written comprehensive repository tests that verify database operations work correctly. **So why test the database again through the API?**

The answer: **You shouldn't (at least not for every test)!** API tests should focus on **HTTP behavior**, not database logic.

### Two Testing Strategies (We'll Use Both!)

**Strategy 1: Unit Tests with Mocked Repositories** (test API layer only)

- ✅ **Fast** - no database operations
- ✅ **Simple** - synchronous tests with `TestClient`
- ✅ **Focused** - tests only HTTP/API concerns
- ✅ **No event loop issues** - works with regular pytest
- ✅ **Repository tests already cover database** - no duplication

**Strategy 2: Integration Tests** (test everything, including database)

- ✅ Tests full stack end-to-end
- ✅ Verifies FastAPI → Repository → Database wiring works
- ❌ Slower (database overhead)
- ❌ Requires async fixtures and `AsyncClient`
- ❌ Event loop complexity with `AsyncSession`

**We'll use both strategies:**

- **Unit tests (70%)**: Fast, focused tests with mocked repositories
- **Integration tests (30%)**: End-to-end verification with real database

Using **pytest markers** (`@pytest.mark.unit` and `@pytest.mark.integration`), we can run them selectively during development.

### Understanding TestClient with Mocked Dependencies

```python
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock

# TestClient wraps your app for testing
client = TestClient(app)

# Mock repository returns test data
mock_repo.get_all.return_value = [model1, model2]

# Make requests like a real client
response = client.get("/api/v1/models/")

# Assert on HTTP behavior
assert response.status_code == 200
assert len(response.json()) == 2
```

**What we're testing:**

- ✅ Routing works (correct endpoint called)
- ✅ Request validation (query parameters, path params)
- ✅ Response serialization (Model → ModelResponse)
- ✅ Status codes (200, 404, 422, etc.)
- ✅ Error handling (HTTPException returns proper JSON)

**What we're NOT testing:**

- ❌ Database queries (already tested in repository tests)
- ❌ Data persistence (already tested in repository tests)
- ❌ Transactions (already tested in repository tests)

### Create API Test Structure

We'll organize tests into two files:

1. `backend/tests/api/conftest.py` - Fixtures specific to API tests
2. `backend/tests/api/test_models.py` - Model endpoint tests (unit + integration)

First, create the API test fixtures in `backend/tests/api/conftest.py`:

```python
import pytest

from datetime import datetime, date

from app.models.models import Model, Benchmark


@pytest.fixture
def sample_model_data():
    """Sample model data for mocked responses (unit tests)"""
    return Model(
        id=1,
        name="gpt-test",
        display_name="GPT Test",
        organization="OpenAI",
        release_date=date(2023, 3, 14),
        description="Most capable GPT Test model",
        created_at=datetime(2024, 1, 1),
        updated_at=datetime(2024, 1, 1),
    )


@pytest.fixture
def sample_models_list(sample_model_data):
    """Sample model instances for mocking repository responses"""
    return [
        sample_model_data,
        Model(
            id=2,
            name="claude-test",
            display_name="Claude Test",
            organization="Anthropic",
            release_date=date(2024, 3, 4),
            description="Most capable Claude Test model",
            created_at=datetime(2025, 1, 2),
            updated_at=datetime(2025, 1, 2),
        ),
        Model(
            id=3,
            name="gemini-test",
            display_name="Gemini Test",
            organization="Google",
            release_date=date(2023, 12, 6),
            description="Advanced reasoning and coding",
            created_at=datetime(2024, 1, 3),
            updated_at=datetime(2024, 1, 3),
        ),
    ]


@pytest.fixture
def sample_benchmarks():
    """Sample benchmark instances for mocking repository responses"""
    return [
        Benchmark(
            id=1,
            name="MMLU",
            category="Knowledge",
            description="Massive Multitask Language Understanding",
            created_at=datetime(2024, 1, 1, 12, 0),
            updated_at=datetime(2024, 1, 1, 12, 0),
        ),
        Benchmark(
            id=2,
            name="HumanEval",
            category="Coding",
            description="Python code generation benchmark",
            created_at=datetime(2024, 1, 2, 12, 0),
            updated_at=datetime(2024, 1, 2, 12, 0),
        ),
        Benchmark(
            id=3,
            name="GSM8K",
            category="Math",
            description="Grade school math problems",
            created_at=datetime(2024, 1, 3, 12, 0),
            updated_at=datetime(2024, 1, 3, 12, 0),
        ),
    ]
```

Now create the actual tests in `backend/tests/api/test_models.py`:

```python
"""
Models API Endpoint Tests

Combines unit tests (mocked repositories) and integration tests (real database)
using pytest markers to distinguish between them.

Unit Tests (70%):
- Test HTTP layer concerns without database
- Fast execution with mocked dependencies
- Focus on routing, validation, serialization

Integration Tests (30%):
- Test end-to-end flows with real database
- Verify FastAPI → Repository → Database wiring
- Validate constraints and relationships

Run specific test types:
    pytest -m unit          # Only unit tests
    pytest -m integration   # Only integration tests
"""

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from app.models.models import Model
from app.db.repositories import ModelRepository


@pytest.mark.unit
class TestModelsEndpointsUnit:
    """Unit tests for /api/v1/models endpoints with mocked repository"""

    @patch("app.api.v1.models.ModelRepository")
    def test_list_models_empty(self, MockRepo: AsyncMock, client: TestClient):
        """Test listing models when database is empty"""
        # Setup mock
        mock_repo_instance = AsyncMock()
        mock_repo_instance.get_all.return_value = []
        MockRepo.return_value = mock_repo_instance

        response = client.get("/api/v1/models/")

        assert response.status_code == 200
        assert response.json() == []
        mock_repo_instance.get_all.assert_awaited_once_with(skip=0, limit=10)

    @patch("app.api.v1.models.ModelRepository")
    def test_list_models_with_data(
        self, MockRepo: AsyncMock, client: TestClient, sample_models_list: list[Model]
    ):
        """Test listing models when database has data"""
        mock_repo_instance = AsyncMock()
        mock_repo_instance.get_all.return_value = sample_models_list
        MockRepo.return_value = mock_repo_instance

        response = client.get("/api/v1/models/")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert data[0]["name"] == "gpt-test"
        assert data[0]["id"] == 1
        mock_repo_instance.get_all.assert_awaited_once_with(skip=0, limit=10)

    @patch("app.api.v1.models.ModelRepository")
    def test_list_models_pagination(
        self, MockRepo: AsyncMock, client: TestClient, sample_models_list: list[Model]
    ):
        """Test pagination parameters are passed to repository"""
        mock_repo_instance = AsyncMock()
        mock_repo_instance.get_all.return_value = sample_models_list[:2]
        MockRepo.return_value = mock_repo_instance

        response = client.get("/api/v1/models/?skip=1&limit=2")

        assert response.status_code == 200
        assert len(response.json()) == 2
        mock_repo_instance.get_all.assert_awaited_once_with(skip=1, limit=2)

    def test_list_models_pagination_invalid_params(self, client: TestClient):
        """Test pagination with invalid parameters returns 422"""
        # Negative skip should fail
        response = client.get("/api/v1/models/?skip=-1")
        assert response.status_code == 422

        # Limit too large should fail
        response = client.get("/api/v1/models/?limit=2000")
        assert response.status_code == 422

    @patch("app.api.v1.models.ModelRepository")
    def test_get_model_by_id(
        self, MockRepo: AsyncMock, client: TestClient, sample_model_data: Model
    ):
        """Test getting a specific model by ID"""
        mock_repo_instance = AsyncMock()
        mock_repo_instance.get_by_id.return_value = sample_model_data
        MockRepo.return_value = mock_repo_instance

        response = client.get(f"/api/v1/models/{sample_model_data.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_model_data.id
        assert data["name"] == sample_model_data.name
        mock_repo_instance.get_by_id.assert_awaited_once_with(sample_model_data.id)

    @patch("app.api.v1.models.ModelRepository")
    def test_get_model_by_id_not_found(self, MockRepo: AsyncMock, client: TestClient):
        """Test getting non-existent model returns 404"""
        # Setup mock to return None (not found)
        mock_repo_instance = AsyncMock()
        mock_repo_instance.get_by_id.return_value = None
        MockRepo.return_value = mock_repo_instance

        response = client.get("/api/v1/models/9999")

        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    @patch("app.api.v1.models.ModelRepository")
    def test_get_model_by_name(
        self, MockRepo: AsyncMock, client: TestClient, sample_model_data: Model
    ):
        """Test getting a model by its unique name"""
        mock_repo_instance = AsyncMock()
        mock_repo_instance.get_by_name.return_value = sample_model_data
        MockRepo.return_value = mock_repo_instance

        response = client.get(f"/api/v1/models/name/{sample_model_data.name}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_model_data.id
        assert data["name"] == sample_model_data.name
        mock_repo_instance.get_by_name.assert_awaited_once_with(sample_model_data.name)

    @patch("app.api.v1.models.ModelRepository")
    def test_get_model_by_name_not_found(self, MockRepo: AsyncMock, client: TestClient):
        """Test getting non-existent model by name returns 404"""
        # Setup mock to return None (not found)
        mock_repo_instance = AsyncMock()
        mock_repo_instance.get_by_name.return_value = None
        MockRepo.return_value = mock_repo_instance

        response = client.get("/api/v1/models/name/nonexistent-model")

        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()


@pytest.mark.integration
class TestModelsEndpointsIntegration:
    """Integration tests for /api/v1/models endpoints with real database"""

    async def test_list_models_with_real_data(
        self,
        client_with_db: AsyncClient,
        test_session: async_sessionmaker[AsyncSession],
        sample_models: list[Model],
    ):
        """Test listing models with real database data"""
        model_repo = ModelRepository(test_session)
        for model in sample_models:
            await model_repo.create(model)

        response = await client_with_db.get("/api/v1/models/")

        assert response.status_code == 200
        data = response.json()

        # Verify that all our test models are in the response
        # (there might be additional models from production database)
        returned_names = {model["name"] for model in data}
        expected_names = {model.name for model in sample_models}
        assert expected_names.issubset(returned_names), (
            f"Expected models {expected_names} not found in response. "
            f"Got: {returned_names}"
        )

    async def test_pagination_with_real_data(
        self,
        client_with_db: AsyncClient,
        test_session: async_sessionmaker[AsyncSession],
        sample_models: list[Model],
    ):
        """Test that pagination works correctly with real database"""
        # Create test models for pagination testing
        model_repo = ModelRepository(test_session)
        created_models = []
        for model in sample_models:
            created_model = await model_repo.create(model)
            created_models.append(created_model)

        # Test first page (skip=0, limit=2)
        response = await client_with_db.get("/api/v1/models/?skip=0&limit=2")
        assert response.status_code == 200
        page1 = response.json()
        assert len(page1) == 2

        # Test second page (skip=2, limit=1)
        response = await client_with_db.get("/api/v1/models/?skip=2&limit=1")
        assert response.status_code == 200
        page2 = response.json()
        assert len(page2) == 1

        # Verify that page1 and page2 don't overlap
        page1_ids = {model["id"] for model in page1}
        page2_ids = {model["id"] for model in page2}
        assert page1_ids.isdisjoint(
            page2_ids
        ), "Pages should not have overlapping models"

    async def test_get_model_by_id_integration(
        self,
        client_with_db: AsyncClient,
        test_session: async_sessionmaker[AsyncSession],
        sample_models: list[Model],
    ):
        """Test retrieving a specific model by ID with real database"""
        # Create a test model using sample data
        model_repo = ModelRepository(test_session)
        test_model = sample_models[0]  # Use first model from fixture
        created_model = await model_repo.create(test_model)

        # Retrieve the model via API
        response = await client_with_db.get(f"/api/v1/models/{created_model.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == created_model.id
        assert data["name"] == created_model.name
        assert data["created_at"] is not None

    async def test_get_model_by_name_integration(
        self,
        client_with_db: AsyncClient,
        test_session: async_sessionmaker[AsyncSession],
        sample_models: list[Model],
    ):
        """Test retrieving a model by its unique name with real database"""
        # Create a test model using sample data
        model_repo = ModelRepository(test_session)
        test_model = sample_models[1]  # Use second model from fixture
        created_model = await model_repo.create(test_model)

        # Retrieve the model by name via API
        response = await client_with_db.get(f"/api/v1/models/name/{created_model.name}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == created_model.id
        assert data["name"] == created_model.name

    async def test_get_nonexistent_model_integration(
        self,
        client_with_db: AsyncClient,
    ):
        """Test that requesting a nonexistent model returns 404"""
        # Use a very large ID that shouldn't exist
        nonexistent_id = 999999999

        response = await client_with_db.get(f"/api/v1/models/{nonexistent_id}")

        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()
        assert str(nonexistent_id) in data["detail"]
```

**Key testing patterns:**

### 1. Test Class Organization with Pytest Markers

```python
@pytest.mark.unit
class TestModelsEndpointsUnit:
    """Unit tests for /api/v1/models endpoints with mocked repository"""

    @patch("app.api.v1.models.ModelRepository")
    def test_list_models_empty(self, MockRepo: AsyncMock, client: TestClient):
        """Test listing models when database is empty"""
        # Setup mock
        mock_repo_instance = AsyncMock()
        mock_repo_instance.get_all.return_value = []
        MockRepo.return_value = mock_repo_instance

        response = client.get("/api/v1/models/")

        assert response.status_code == 200
        assert response.json() == []
        mock_repo_instance.get_all.assert_awaited_once_with(skip=0, limit=10)
```

**How it works:**

- `@pytest.mark.unit` marks this as a unit test class
- Allows running only unit tests with: `pytest -m unit`
- `@patch("app.api.v1.models.ModelRepository")` replaces `ModelRepository` class
- `MockRepo` is the mocked class (first parameter in method signature)
- `AsyncMock()` creates a mock that works with async methods
- `.return_value` sets what the mock returns when called
- `.assert_awaited_once_with()` verifies the async mock was called correctly with expected params

**Why this is powerful:**

- ✅ No database operations - tests run instantly
- ✅ Full control over return values - test edge cases easily
- ✅ Verify correct parameters passed to repository
- ✅ Simple synchronous tests - no async complexity

### 2. Separate Fixtures for Unit vs Integration Tests

**Unit test fixtures** (in `tests/api/conftest.py`):

```python
@pytest.fixture
def sample_model_data():
    """Single model for unit tests"""
    return Model(
        id=1,
        name="gpt-test",
        display_name="GPT Test",
        organization="OpenAI",
        created_at=datetime(2024, 1, 1),
        updated_at=datetime(2024, 1, 1),
    )

@pytest.fixture
def sample_models_list(sample_model_data):
    """List of models for unit tests - reuses sample_model_data"""
    return [
        sample_model_data,
        Model(id=2, name="claude-test", ...),
        Model(id=3, name="gemini-test", ...),
    ]
```

**Integration test fixtures** (in `tests/conftest.py`):

```python
@pytest.fixture
def sample_models():
    """Models for integration tests - no IDs (database generates them)"""
    return [
        Model(name="gpt-model-1", display_name="GPT Model 1", ...),
        Model(name="claude-model-2", display_name="Model 2", ...),
        Model(name="gpt-model-3", display_name="GPT Model 3", ...),
    ]
```

**Key differences:**

- **Unit test fixtures**: Include IDs and timestamps (simulate database records)
- **Integration test fixtures**: No IDs (database auto-generates them)
- **Unit fixtures**: In `tests/api/conftest.py` (local to API tests)
- **Integration fixtures**: In `tests/conftest.py` (shared across all tests)

### 3. Integration Tests with AsyncClient

```python
@pytest.mark.integration
class TestModelsEndpointsIntegration:
    """Integration tests for /api/v1/models endpoints with real database"""

    async def test_list_models_with_real_data(
        self,
        client_with_db: AsyncClient,
        test_session: async_sessionmaker[AsyncSession],
        sample_models: list[Model],
    ):
        """Test listing models with real database data"""
        model_repo = ModelRepository(test_session)
        for model in sample_models:
            await model_repo.create(model)

        response = await client_with_db.get("/api/v1/models/")

        assert response.status_code == 200
        data = response.json()

        # Verify our test models are in the response
        returned_names = {model["name"] for model in data}
        expected_names = {model.name for model in sample_models}
        assert expected_names.issubset(returned_names)
```

**Key patterns for integration tests:**

- Use `@pytest.mark.integration` to mark integration tests
- Use `AsyncClient` (not `TestClient`) for async tests
- Use `client_with_db` fixture that overrides `get_db` dependency
- Use `test_session` fixture for database operations
- Tests are `async def` (not regular `def`)
- Use `await` for HTTP requests and repository calls

**What integration tests verify:**

- ✅ Full stack works end-to-end (FastAPI → Repository → Database)
- ✅ Dependency injection wiring is correct
- ✅ Database constraints and relationships work
- ✅ Actual SQL queries return expected results

### 4. Validation Tests (No Mocking Needed)

```python
def test_list_models_pagination_invalid_params(self, client: TestClient):
    """Test pagination with invalid parameters returns 422"""
    # Negative skip should fail
    response = client.get("/api/v1/models/?skip=-1")
    assert response.status_code == 422

    # Limit too large should fail
    response = client.get("/api/v1/models/?limit=2000")
    assert response.status_code == 422
```

**No mocking needed:**

- FastAPI validates before calling repository
- Tests routing + parameter validation only
- Super fast - no database, no mocking
- Part of unit test class but doesn't need `@patch`

### 5. Verifying Mock Calls with assert_awaited_once_with

```python
@patch("app.api.v1.models.ModelRepository")
def test_list_models_pagination(
    self, MockRepo: AsyncMock, client: TestClient, sample_models_list: list[Model]
):
    """Test pagination parameters are passed to repository"""
    mock_repo_instance = AsyncMock()
    mock_repo_instance.get_all.return_value = sample_models_list[:2]
    MockRepo.return_value = mock_repo_instance

    response = client.get("/api/v1/models/?skip=1&limit=2")

    assert response.status_code == 200
    assert len(response.json()) == 2
    # Verify repository was called with correct params
    mock_repo_instance.get_all.assert_awaited_once_with(skip=1, limit=2)
```

**Why this matters:**

- `.assert_awaited_once_with()` verifies async method was called exactly once
- Ensures endpoint passes parameters correctly to repository
- Catches bugs where parameters are ignored or transformed incorrectly
- Documents the expected repository interface
- Different from `.assert_called_once_with()` which is for sync methods

### Run the API Tests

With our organized test structure, we can run different test types selectively:

**Run all tests:**

```bash
cd backend
uv run pytest tests/api/test_models.py -v
```

**Run only unit tests (fast!):**

```bash
uv run pytest tests/api/test_models.py -m unit -v
```

**Run only integration tests:**

```bash
uv run pytest tests/api/test_models.py -m integration -v
```

**Expected output for unit tests:**

```
tests/api/test_models.py::TestModelsEndpointsUnit::test_list_models_empty PASSED
tests/api/test_models.py::TestModelsEndpointsUnit::test_list_models_with_data PASSED
tests/api/test_models.py::TestModelsEndpointsUnit::test_list_models_pagination PASSED
tests/api/test_models.py::TestModelsEndpointsUnit::test_list_models_pagination_invalid_params PASSED
tests/api/test_models.py::TestModelsEndpointsUnit::test_get_model_by_id PASSED
tests/api/test_models.py::TestModelsEndpointsUnit::test_get_model_by_id_not_found PASSED
tests/api/test_models.py::TestModelsEndpointsUnit::test_get_model_by_name PASSED
tests/api/test_models.py::TestModelsEndpointsUnit::test_get_model_by_name_not_found PASSED
====== 8 passed in 0.12s ======
```

**Notice how fast unit tests run!** No database connection, no async complexity - just pure HTTP behavior testing.

**Expected output for integration tests:**

```
tests/api/test_models.py::TestModelsEndpointsIntegration::test_list_models_with_real_data PASSED
tests/api/test_models.py::TestModelsEndpointsIntegration::test_pagination_with_real_data PASSED
tests/api/test_models.py::TestModelsEndpointsIntegration::test_get_model_by_id_integration PASSED
tests/api/test_models.py::TestModelsEndpointsIntegration::test_get_model_by_name_integration PASSED
tests/api/test_models.py::TestModelsEndpointsIntegration::test_get_nonexistent_model_integration PASSED
====== 5 passed in 2.34s ======
```

Integration tests take longer due to database operations, but verify the full stack works end-to-end.

**When to run each type:**

- **During development**: Run unit tests (`-m unit`) for quick feedback
- **Before commits**: Run all tests to ensure everything works
- **In CI/CD**: Run all tests with coverage reporting
- **Debugging**: Run specific test with `-k test_name`

**🎯 Checkpoint:** Your API has fast unit tests (70%) and comprehensive integration tests (30%), organized with pytest markers!

---

## Step 8: Understanding OpenAPI Documentation

FastAPI automatically generates OpenAPI (Swagger) documentation from your code. Let's understand what's happening.

### What is OpenAPI?

**OpenAPI Specification** is a standard format for describing REST APIs. It includes:

- Available endpoints
- Request/response schemas
- Parameter types and validation
- Authentication methods
- Example values

### How FastAPI Generates Docs

FastAPI analyzes your code:

```python
@router.get("/", response_model=list[ModelResponse])
async def list_models(
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=20, le=100),
    session: AsyncSession = Depends(get_db),
) -> Sequence[ModelResponse]:
    """
    List all AI models with pagination.

    - **skip**: Number of records to skip
    - **limit**: Maximum records to return
    """
```

**What gets extracted:**

1. **Endpoint**: `GET /api/v1/models/`
2. **Response schema**: `list[ModelResponse]` with all its fields
3. **Query parameters**: `skip` (int, >= 0, default 0), `limit` (int, <= 100, default 20)
4. **Description**: From the docstring
5. **Parameter docs**: From `description` and docstring markdown
6. **Tags**: From router configuration

### Enhancing Documentation

You can add rich details:

```python
@router.get(
    "/{model_id}",
    response_model=ModelResponse,
    summary="Get a model by ID",
    description="Retrieve detailed information about a specific AI model",
    responses={
        200: {
            "description": "Model found and returned",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "name": "gpt-4",
                        "organization": "OpenAI",
                    }
                }
            }
        },
        404: {"description": "Model not found"},
    }
)
async def get_model(model_id: int, ...):
    """..."""
```

**Advanced features:**

- Custom examples
- Multiple response schemas for different status codes
- Deprecation notices
- Security requirements

### Using the OpenAPI JSON

The spec is available at `http://localhost:8000/openapi.json`. You can:

- **Generate client libraries** (TypeScript, Python, Go) with tools like `openapi-generator`
- **Import into Postman** for API testing
- **Generate documentation sites** with tools like Redocly
- **Validate requests** in other languages

**Example - Generate TypeScript client:**

```bash
npx @openapitools/openapi-generator-cli generate \
  -i http://localhost:8000/openapi.json \
  -g typescript-axios \
  -o frontend/src/api/generated
```

This creates type-safe TypeScript functions for every endpoint!

**🎯 Checkpoint:** You understand how FastAPI generates documentation and how to enhance it.

---

## Understanding the Complete Request/Response Flow

Let's trace a request through your entire stack to solidify understanding.

### Example: GET /api/v1/models/1

**1. Client makes request:**

```bash
curl http://localhost:8000/api/v1/models/1
```

**2. FastAPI routing:**

- Matches route: `GET /api/v1/models/{model_id}`
- Extracts path parameter: `model_id = 1`

**3. Dependency injection:**

- Sees `session: AsyncSession = Depends(get_db)`
- Calls `get_db()` which yields a database session
- Creates `AsyncSession` from pool

**4. Function execution:**

```python
async def get_model(model_id: int, session: AsyncSession = Depends(get_db)):
    repo = ModelRepository(session)  # Create repo
    model = await repo.get_by_id(model_id)  # Query database
```

**5. Repository query:**

```python
# In ModelRepository
async def get_by_id(self, id: int) -> Model | None:
    return await self.session.get(Model, id)
```

**6. Database query:**

```sql
SELECT * FROM models WHERE id = 1;
```

**7. Result returned:**

- Database returns row
- SQLAlchemy creates `Model` instance
- Repository returns `Model` to endpoint

**8. Response validation:**

- FastAPI sees `response_model=ModelResponse`
- Converts `Model` → `ModelResponse` (removes relationships, validates schema)

**9. JSON serialization:**

- Pydantic converts `ModelResponse` to dict
- FastAPI serializes to JSON
- Sets `Content-Type: application/json`

**10. HTTP response:**

```json
{
  "id": 1,
  "name": "gpt-4",
  "display_name": "GPT-4",
  "organization": "OpenAI",
  "release_date": "2023-03-14",
  "description": "Most capable GPT-4 model",
  "license": null,
  "metadata_": null,
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00"
}
```

**11. Cleanup:**

- `get_db()` context manager closes
- Session returned to pool
- Request complete

**The layers:**

```
HTTP Request
    ↓
FastAPI Router (routing, validation)
    ↓
Endpoint Function (business logic)
    ↓
Repository (data access)
    ↓
Database (storage)
    ↓
Repository (model creation)
    ↓
Endpoint (returns model)
    ↓
FastAPI (validation, serialization)
    ↓
HTTP Response
```

**Each layer has a clear job:**

- **Router**: Routing and parameter extraction
- **Endpoint**: HTTP concerns (status codes, errors)
- **Repository**: Database queries
- **Database**: Data storage

**🎯 Checkpoint:** You understand the complete request lifecycle in your application.

---

## Common Pitfalls and How to Avoid Them

### Pitfall 1: Forgetting response_model

**Symptom:**

```python
# ❌ No response_model
@router.get("/")
async def list_models(...):
    return models  # Returns Model objects (database models)
```

**Problem:**

- Exposes database relationships (benchmark_results, opinions)
- No validation (programming errors become API errors)
- Heavy responses (includes all related data)

**Solution:**

```python
# ✅ With response_model
@router.get("/", response_model=list[ModelResponse])
async def list_models(...):
    return models  # FastAPI converts to ModelResponse
```

### Pitfall 2: Not Using Depends for Database Sessions

**Symptom:**

```python
# ❌ Manual session management
@router.get("/")
async def list_models():
    async with AsyncSessionLocal() as session:
        repo = ModelRepository(session)
        return await repo.get_all()
    # Session closed, but what if an exception occurred?
```

**Problems:**

- Hard to test (can't inject test session)
- Need try/finally everywhere
- Can't share session across multiple repository calls
- Verbose

**Solution:**

```python
# ✅ Dependency injection
@router.get("/")
async def list_models(session: AsyncSession = Depends(get_db)):
    repo = ModelRepository(session)
    return await repo.get_all()
# FastAPI handles session lifecycle
```

### Pitfall 3: Returning Database Models Directly

**Symptom:**

```python
# ❌ Returning Model (database model)
@router.get("/{id}")
async def get_model(id: int, session: AsyncSession = Depends(get_db)):
    model = await ModelRepository(session).get_by_id(id)
    return model  # Includes relationships!
```

**What happens:**

- FastAPI tries to serialize relationships
- Can trigger lazy loading (N+1 queries)
- Circular references cause errors
- Exposes too much data

**Solution:**

```python
# ✅ Use response_model to control what's exposed
@router.get("/{id}", response_model=ModelResponse)
async def get_model(id: int, session: AsyncSession = Depends(get_db)):
    model = await ModelRepository(session).get_by_id(id)
    return model  # FastAPI converts to ModelResponse
```

### Pitfall 4: Missing Error Handling

**Symptom:**

```python
# ❌ No error handling
@router.get("/{id}")
async def get_model(id: int, ...):
    model = await repo.get_by_id(id)
    return model  # Returns None if not found! (200 OK with null)
```

**Problem:**

- Client gets `null` instead of 404
- Unclear error states
- Violates REST conventions

**Solution:**

```python
# ✅ Explicit error handling
@router.get("/{id}", response_model=ModelResponse)
async def get_model(id: int, ...):
    model = await repo.get_by_id(id)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    return model
```

### Pitfall 5: Not Validating Query Parameters

**Symptom:**

```python
# ❌ No validation
@router.get("/")
async def list_models(skip: int = 0, limit: int = 100, ...):
    # What if skip is -10? Or limit is 1000000?
```

**Problems:**

- Negative skip breaks queries
- Massive limit kills performance
- Type errors with non-integers

**Solution:**

```python
# ✅ Validated parameters
@router.get("/")
async def list_models(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, le=100),
    ...
):
```

### Pitfall 6: Inconsistent Status Codes

**Symptom:**

```python
# ❌ Always returns 200
@router.post("/")
async def create_model(...):
    created = await repo.create(model)
    return created  # Returns 200 instead of 201
```

**Problem:**

- REST convention: POST should return 201 Created
- Confusing for clients
- Harder to distinguish operations

**Solution:**

```python
# ✅ Explicit status code
@router.post("/", response_model=ModelResponse, status_code=201)
async def create_model(...):
    created = await repo.create(model)
    return created  # Returns 201 Created
```

**🎯 Checkpoint:** You know the common mistakes and how to avoid them.

---

## What You've Accomplished

Congratulations! You've built a professional API foundation. Here's what you now have:

### 1. Complete API Layer

- ✅ **Routers organized by domain** (models, benchmarks)
- ✅ **RESTful endpoint design** following conventions
- ✅ **Proper HTTP methods and status codes**
- ✅ **Pagination and filtering** built-in

### 2. Request/Response Schemas

- ✅ **SQLModel schemas** leveraging inheritance to reduce duplication
- ✅ **Input validation** on all requests
- ✅ **Response models** controlling what's exposed
- ✅ **Type safety** throughout the stack

### 3. Dependency Injection

- ✅ **Database session management** via FastAPI dependencies
- ✅ **Testable architecture** with dependency overrides
- ✅ **Clean separation** of concerns

### 4. Automatic Documentation

- ✅ **OpenAPI/Swagger UI** at `/docs`
- ✅ **ReDoc** at `/redoc`
- ✅ **Interactive testing** of endpoints
- ✅ **Schema documentation** auto-generated

### 5. Comprehensive Testing

- ✅ **19 API tests** covering all endpoints
- ✅ **TestClient** for fast, isolated testing
- ✅ **Dependency overrides** for test database
- ✅ **Schema validation** tests

### 6. Professional Patterns

- ✅ **Error handling** with HTTPException
- ✅ **Query parameter validation** with Query
- ✅ **Consistent response format**
- ✅ **Version-prefixed URLs** (/api/v1/)

---

## Key Takeaways

**On API Design:**

- **Schemas are contracts** - they define what your API promises to clients
- **SQLModel reduces duplication** - inherit from base models to share field definitions
- **response_model is essential** - it validates responses and controls what's exposed
- **REST conventions make APIs predictable** - follow standard patterns

**On FastAPI Patterns:**

- **Routers organize code** - one router per domain (models, benchmarks, users)
- **Dependency injection is powerful** - `Depends()` manages resources cleanly
- **Query() validates parameters** - set constraints (ge, le) to prevent bad inputs
- **Documentation is automatic** - docstrings and type hints generate OpenAPI specs

**On Testing:**

- **TestClient is fast** - test without starting a server
- **dependency_overrides enable testing** - swap production dependencies for test ones
- **Test scenarios comprehensively** - empty states, happy paths, error cases
- **Schema tests catch bugs** - verify responses match expected structure

**On Architecture:**

- **Layers stay separated** - API → Repository → Database
- **Each layer has one job** - routing, business logic, or data access
- **Type safety cascades** - from database to API response
- **Changes are localized** - modify repositories without touching endpoints

---

## What's Next?

In **Module 2.2: CRUD Endpoints & Error Handling**, you'll:

- **Implement POST, PUT, DELETE** operations for all resources
- **Add comprehensive error handling** with custom exception handlers
- **Build validation logic** in endpoints (checking for duplicates, etc.)
- **Create related resource endpoints** (`/models/{id}/benchmarks`)
- **Add search functionality** using repository search methods
- **Learn transaction management** for multi-step operations
- **Implement request logging** for debugging
- **Add rate limiting** (optional advanced topic)

You've built the foundation. Now it's time to add full CRUD capabilities and polish your API to production quality!

---

## Hands-On Exercise

Before moving to the next module, solidify your learning with these exercises:

### Exercise 1: Add GET Endpoint for BenchmarkResults

Implement a new endpoint: `GET /api/v1/models/{model_id}/benchmarks`

**Requirements:**

- Return all benchmark results for a specific model
- Include the benchmark details in the response (eager loading)
- Return 404 if model doesn't exist
- Add pagination (skip, limit)

**Acceptance Criteria:**

- New router function in `models.py`
- Uses `BenchmarkResultRepository.get_by_model_id()`
- Proper error handling
- Tests in `test_api.py`

**Hints:**

- Use `selectinload()` to load benchmark relationships
- Return `list[BenchmarkResultResponse]`
- Check if model exists before querying results

### Exercise 2: Add Search Endpoint

Implement: `GET /api/v1/models/search?q=openai`

**Requirements:**

- Use `ModelRepository.search()` from Module 1.2
- Accept query parameter `q` for search term
- Support pagination
- Return empty list if no matches

**Acceptance Criteria:**

- New endpoint in models router
- Query validation (minimum 2 characters)
- Case-insensitive search
- Tests covering various search terms

### Exercise 3: Enhance API Documentation

Improve the documentation for the models router:

**Tasks:**

- Add detailed docstrings with parameter descriptions
- Add example responses in OpenAPI
- Add deprecation notice to an endpoint (practice for future versions)
- Create a summary and description for the router

**Acceptance Criteria:**

- Visit `/docs` and see enhanced descriptions
- Parameters show clear explanations
- Example values appear in the UI

### Exercise 4: Create Opinion and UseCase Routers

Following the patterns from models and benchmarks, create routers for:

- `app/api/v1/opinions.py`
- `app/api/v1/use_cases.py`

**Requirements:**

- List endpoints with pagination
- Get by ID endpoints
- Filter by model_id
- Proper error handling
- Complete test coverage

**Acceptance Criteria:**

- Routers included in `main.py`
- All endpoints return proper status codes
- Tests verify functionality
- Documentation appears in `/docs`

---

## Additional Resources

### FastAPI Documentation

- [FastAPI Official Docs](https://fastapi.tiangolo.com/) - Comprehensive guide
- [Dependency Injection in FastAPI](https://fastapi.tiangolo.com/tutorial/dependencies/)
- [Response Models](https://fastapi.tiangolo.com/tutorial/response-model/)
- [Query Parameters](https://fastapi.tiangolo.com/tutorial/query-params/)

### SQLModel & Pydantic

- [SQLModel Docs](https://sqlmodel.tiangolo.com/) - Official guide
- [Pydantic Validation](https://docs.pydantic.dev/latest/concepts/validators/)
- [Schema Design Patterns](https://sqlmodel.tiangolo.com/tutorial/fastapi/simple-hero-api/)

### REST API Design

- [REST API Tutorial](https://restfulapi.net/) - Best practices
- [HTTP Status Codes](https://httpstatuses.com/) - Complete reference
- [API Design Patterns](https://swagger.io/resources/articles/best-practices-in-api-design/)

### OpenAPI Specification

- [OpenAPI Specification](https://swagger.io/specification/) - Official spec
- [Swagger Editor](https://editor.swagger.io/) - Interactive editor
- [API Client Generation](https://openapi-generator.tech/) - Generate clients

### Testing

- [FastAPI Testing Guide](https://fastapi.tiangolo.com/tutorial/testing/)
- [TestClient Documentation](https://fastapi.tiangolo.com/reference/testclient/)
- [pytest Best Practices](https://docs.pytest.org/en/stable/goodpractices.html)

---

**Ready for more?** Head to Module 2.2 to implement full CRUD operations and advanced error handling!
