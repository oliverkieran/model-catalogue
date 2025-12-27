# Module 2.2: CRUD Operations & Error Handling - Building Production-Quality APIs

**Duration:** 2-3 hours
**Difficulty:** Intermediate
**Prerequisites:** Module 2.1 (SQLModel Schemas & API Foundation) complete

---

## Introduction: From Read-Only to Full CRUD

In Module 2.1, you built the foundation: GET endpoints that read data from your database. Your API can list models, retrieve them by ID, and filter by category. This is great for displaying data, but **real applications need to create, update, and delete data too**.

Here's the exciting part: you already have 80% of what you need! Your repository layer has full CRUD methods, your schemas are ready, and your routing infrastructure is in place. In this module, you'll connect the dots and build a **production-quality API** that handles:

- **Creating resources** (POST requests)
- **Updating resources** (PUT/PATCH requests)
- **Deleting resources** (DELETE requests)
- **Validating input** (preventing duplicates, checking references)
- **Handling errors gracefully** (clear HTTP responses)
- **Managing related resources** (nested endpoints like `/models/{id}/benchmarks`)
- **Searching and filtering** (query-based operations)

**But here's a critical question: What makes a CRUD API "production-quality"?**

```python
# ❌ Naive approach (works but dangerous)
@router.post("/")
async def create_model(model: ModelCreate, session: AsyncSession = Depends(get_db)):
    new_model = Model(**model.dict())
    session.add(new_model)
    await session.commit()
    return new_model
```

**What's wrong with this?**

- **No duplicate checking**: Creating "gpt-4" twice causes database errors
- **No validation**: Invalid data passes through unchecked
- **Poor error messages**: Users see raw database errors
- **No status code**: Returns 200 instead of 201 Created
- **No error handling**: Crashes on database failures
- **No transaction management**: Partial failures leave inconsistent data

**The production approach:**

```python
# ✅ Production-quality approach
@router.post("/", response_model=ModelResponse, status_code=201)
async def create_model(
    model_data: ModelCreate,
    session: AsyncSession = Depends(get_db),
):
    """
    Create a new AI model with validation and error handling.

    Checks for duplicate names before creation and returns detailed
    error messages if validation fails.
    """
    # Check for duplicates
    repo = ModelRepository(session)
    existing = await repo.get_by_name(model_data.name)
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"Model with name '{model_data.name}' already exists"
        )

    # Create the model
    try:
        new_model = Model(**model_data.model_dump())
        created = await repo.create(new_model)
        return created
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create model: {str(e)}"
        )
```

**What makes this better?**

- ✅ **Duplicate prevention**: Checks if name exists before creating
- ✅ **Proper status codes**: Returns 201 Created, 409 Conflict, 500 Error
- ✅ **Clear error messages**: Tells users exactly what went wrong
- ✅ **Comprehensive validation**: Uses Pydantic schemas for input validation
- ✅ **Graceful error handling**: Catches exceptions and returns clear errors
- ✅ **Transaction safety**: Repository pattern ensures atomic operations

In this module, you'll learn:

- **Implementing POST, PUT, DELETE** operations following REST conventions
- **Comprehensive error handling** with clear HTTP responses
- **Input validation patterns** (duplicate checking, reference validation)
- **Related resource endpoints** (getting a model's benchmarks)
- **Search functionality** using repository search methods
- **Transaction management** for multi-step operations
- **Testing CRUD operations** with focused unit tests

By the end, you'll have a **complete, production-ready API** that handles real-world scenarios gracefully.

---

## What You'll Build

By the end of this module, you'll have:

- ✅ Complete CRUD operations for Models (POST, PUT, DELETE)
- ✅ Complete CRUD operations for Benchmarks
- ✅ BenchmarkResults creation and management
- ✅ Clear, consistent error responses for CRUD operations
- ✅ Duplicate checking and validation logic
- ✅ Related resource endpoints (`/models/{id}/benchmarks`)
- ✅ Search endpoints with query-based filtering
- ✅ Focused unit tests for Models CRUD
- ✅ Transaction management for complex operations
- ✅ Professional error messages and status codes

---

## Understanding CRUD Conventions

Before we code, let's understand the conventions that make APIs predictable.

### The CRUD-to-HTTP Mapping

REST APIs map CRUD operations to HTTP methods:

```
CREATE  →  POST /api/v1/models          (Create new resource)
READ    →  GET  /api/v1/models/{id}     (Read one resource)
READ    →  GET  /api/v1/models          (Read multiple resources)
UPDATE  →  PUT  /api/v1/models/{id}     (Replace entire resource)
UPDATE  →  PATCH /api/v1/models/{id}    (Update partial resource)
DELETE  →  DELETE /api/v1/models/{id}   (Remove resource)
```

**Key differences:**

- **POST**: Creates new resource, returns 201 Created with new ID
- **PUT**: Replaces entire resource, requires all fields
- **PATCH**: Updates partial resource, only specified fields changed
- **DELETE**: Removes resource, returns 204 No Content or 200 with deleted entity

### HTTP Status Codes for CRUD

Professional APIs use specific status codes for each operation:

```python
# CREATE operations
201 Created          # Successfully created new resource
400 Bad Request      # Invalid input data
409 Conflict         # Resource already exists (duplicate)
422 Unprocessable    # Validation failed (FastAPI default)

# READ operations
200 OK              # Successfully retrieved resource(s)
404 Not Found       # Resource doesn't exist

# UPDATE operations
200 OK              # Successfully updated and returning resource
204 No Content      # Successfully updated, no response body
404 Not Found       # Resource doesn't exist
409 Conflict        # Update would create duplicate

# DELETE operations
204 No Content      # Successfully deleted (standard)
200 OK              # Successfully deleted (with response body)
404 Not Found       # Resource doesn't exist
409 Conflict        # Cannot delete (has dependencies)
```

### Request/Response Schema Patterns

Remember from Module 2.1, you have different schemas for different operations:

```python
# CREATE - what users send
class ModelCreate(ModelBase):
    """No ID, no timestamps - those are generated"""
    metadata_: dict | None = None

# UPDATE - all fields optional
class ModelUpdate(SQLModel):
    """All fields optional for partial updates"""
    name: str | None = None
    display_name: str | None = None
    # ... all fields optional

# RESPONSE - what API returns
class ModelResponse(ModelBase):
    """Includes generated fields"""
    id: int
    metadata_: dict | None = None
    created_at: datetime
    updated_at: datetime
```

**Why this structure?**

- **Create schemas**: Users can't set ID or timestamps
- **Update schemas**: Optional fields allow partial updates
- **Response schemas**: Include server-generated fields

**🎯 Checkpoint:** You understand how CRUD operations map to HTTP methods and status codes.

---

## Step 1: Implementing POST - Creating Resources

Let's start by adding creation endpoints to your Models router.

### Understanding the Create Flow

**The creation workflow:**

1. **Client sends POST** with `ModelCreate` data
2. **FastAPI validates** against `ModelCreate` schema (automatic)
3. **Endpoint checks** for duplicates and business rule violations
4. **Repository creates** the entity in the database
5. **Endpoint returns** 201 Created with `ModelResponse`

### Add Create Endpoint to Models Router

Update `backend/app/api/v1/models.py` to add the create endpoint:

```python
# Add to existing imports
from app.models.models import Model, ModelCreate, ModelResponse

# Add after the existing endpoints

@router.post("/", response_model=ModelResponse, status_code=201)
async def create_model(
    model_data: ModelCreate,
    session: AsyncSession = Depends(get_db),
) -> ModelResponse:
    """
    Create a new AI model.

    This endpoint creates a new model in the database after validating
    that no duplicate model names exist.

    Args:
        model_data: Model information (name, organization, description, etc.)

    Returns:
        The created model with generated ID and timestamps

    Raises:
        HTTPException 409: If a model with the same name already exists
        HTTPException 400: If input validation fails
        HTTPException 500: If database operation fails
    """
    repo = ModelRepository(session)

    # Check for duplicate name
    existing = await repo.get_by_name(model_data.name)
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"Model with name '{model_data.name}' already exists with ID {existing.id}"
        )

    # Create the model
    try:
        new_model = Model(**model_data.model_dump())
        created = await repo.create(new_model)
        return created
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create model: {str(e)}"
        )
```

**Let's break down the key patterns:**

### 1. Status Code 201 Created

```python
@router.post("/", response_model=ModelResponse, status_code=201)
```

**Why 201 instead of 200?**

- REST convention: POST for creation returns 201
- Signals "new resource created" vs "existing resource returned"
- Can include `Location` header with new resource URL (optional)

### 2. Duplicate Checking

```python
existing = await repo.get_by_name(model_data.name)
if existing:
    raise HTTPException(
        status_code=409,
        detail=f"Model with name '{model_data.name}' already exists with ID {existing.id}"
    )
```

**Why check before creating?**

- **User-friendly errors**: "Model already exists" vs cryptic database error
- **409 Conflict**: Standard status for duplicate resources
- **Informative messages**: Include existing ID so users can find it
- **Early validation**: Fails fast before database operation

**Alternative: Let database handle it**

```python
# Your Model has unique constraint on name, so database will reject duplicates
# But the error message is less user-friendly:
# "duplicate key value violates unique constraint 'models_name_key'"
```

### 3. Schema Conversion

```python
new_model = Model(**model_data.model_dump())
```

**What's happening:**

- `model_data` is `ModelCreate` (Pydantic schema)
- `Model` is the database table model
- `.model_dump()` converts Pydantic model to dict
- `**` unpacks dict as keyword arguments
- Creates `Model` instance ready for database

**Why not use ModelCreate directly?**

- Repository expects table model (`Model`), not schema (`ModelCreate`)
- Separates API layer (schemas) from data layer (models)
- Allows transformations if needed (e.g., hashing passwords)

### 4. Error Handling

```python
try:
    created = await repo.create(new_model)
    return created
except Exception as e:
    raise HTTPException(status_code=500, detail=f"Failed to create model: {str(e)}")
```

**Why catch exceptions?**

- **Graceful degradation**: Database errors don't crash the server
- **Consistent error format**: All errors return JSON with `detail` field
- **500 Internal Server Error**: Signals unexpected problem
- **Logging opportunity**: Can log errors for debugging (we'll add this later)

**Production tip:** Don't expose raw exception messages to clients in production (security risk). Use generic message and log details server-side.

### Test the Create Endpoint

Let's test it interactively before writing automated tests.

**Start the server:**

```bash
cd backend
uv run uvicorn app.main:app --reload
```

**Using curl:**

```bash
# Create a new model
curl -X POST http://localhost:8000/api/v1/models/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "gpt-4-test",
    "display_name": "GPT-4 Test",
    "organization": "OpenAI",
    "release_date": "2023-03-14",
    "description": "Most capable GPT-4 model",
    "license": "Proprietary"
  }'
```

**Expected response (201 Created):**

```json
{
  "id": 1,
  "name": "gpt-4-test",
  "display_name": "GPT-4 Test",
  "organization": "OpenAI",
  "release_date": "2023-03-14",
  "description": "Most capable GPT-4 model",
  "license": "Proprietary",
  "metadata_": null,
  "created_at": "2025-01-15T10:30:00",
  "updated_at": "2025-01-15T10:30:00"
}
```

**Try creating duplicate (should fail):**

```bash
# Same request again
curl -X POST http://localhost:8000/api/v1/models/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "gpt-4-test",
    "display_name": "GPT-4 Test",
    "organization": "OpenAI"
  }'
```

**Expected response (409 Conflict):**

```json
{
  "detail": "Model with name 'gpt-4-test' already exists with ID 1"
}
```

**Using Swagger UI:**

1. Go to http://localhost:8000/docs
2. Find `POST /api/v1/models/`
3. Click "Try it out"
4. Enter JSON in the request body
5. Click "Execute"
6. See response with status code

**🎯 Checkpoint:** You can create new models via POST requests with duplicate checking!

---

## Step 2: Implementing PUT/PATCH - Updating Resources

Now let's add the ability to update existing resources.

### Understanding PUT vs PATCH

**PUT (full replacement):**

```python
# Client must send ALL fields
PUT /api/v1/models/1
{
  "name": "gpt-4-turbo",
  "display_name": "GPT-4 Turbo",
  "organization": "OpenAI",
  "release_date": "2024-04-01",
  "description": "Faster GPT-4",
  "license": "Proprietary"
}
```

**PATCH (partial update):**

```python
# Client sends only fields to change
PATCH /api/v1/models/1
{
  "description": "Updated description"
}
# All other fields remain unchanged
```

**Which should you use?**

- **Most APIs prefer PATCH** because it's more flexible
- **PUT is simpler** but requires sending entire resource
- **We'll implement PATCH** since our `ModelUpdate` schema has all optional fields

### Add Update Endpoint

Add to `backend/app/api/v1/models.py`:

```python
# Add to imports
from app.models.models import ModelUpdate

# Add after create endpoint

@router.patch("/{model_id}", response_model=ModelResponse)
async def update_model(
    model_id: int,
    model_data: ModelUpdate,
    session: AsyncSession = Depends(get_db),
) -> ModelResponse:
    """
    Update an existing AI model (partial update).

    Only fields provided in the request will be updated. All fields are optional.

    Args:
        model_id: The unique identifier of the model to update
        model_data: Fields to update (all optional)

    Returns:
        The updated model with new values

    Raises:
        HTTPException 404: If model with given ID doesn't exist
        HTTPException 409: If updating name would create duplicate
        HTTPException 400: If input validation fails
    """
    repo = ModelRepository(session)

    # Check if model exists
    existing = await repo.get_by_id(model_id)
    if not existing:
        raise HTTPException(
            status_code=404,
            detail=f"Model with id {model_id} not found"
        )

    # If updating name, check for duplicates (exclude current model)
    update_dict = model_data.model_dump(exclude_unset=True)
    if "name" in update_dict and update_dict["name"] != existing.name:
        duplicate = await repo.get_by_name(update_dict["name"])
        if duplicate:
            raise HTTPException(
                status_code=409,
                detail=f"Model with name '{update_dict['name']}' already exists with ID {duplicate.id}"
            )

    # Update the model with provided fields
    for field, value in update_dict.items():
        setattr(existing, field, value)

    try:
        updated = await repo.update(existing)
        return updated
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update model: {str(e)}"
        )
```

**Key patterns in update operations:**

### 1. Checking Resource Exists

```python
existing = await repo.get_by_id(model_id)
if not existing:
    raise HTTPException(status_code=404, detail=f"Model with id {model_id} not found")
```

**Why check first?**

- Returns 404 if resource doesn't exist (proper HTTP semantics)
- Gets current values for comparison
- Ensures we're updating the right resource

### 2. Partial Update Pattern

```python
update_dict = model_data.model_dump(exclude_unset=True)
```

**What is `exclude_unset=True`?**

- Only includes fields that were **explicitly provided** in the request
- Excludes fields with default values that weren't set
- Enables partial updates

**Example:**

```python
# Request: {"description": "New description"}
model_data = ModelUpdate(description="New description")

# Without exclude_unset
model_data.model_dump()
# → {"name": None, "display_name": None, "description": "New description", ...}
# Would set all fields to None!

# With exclude_unset=True
model_data.model_dump(exclude_unset=True)
# → {"description": "New description"}
# Only includes fields actually provided
```

### 3. Conditional Duplicate Checking

```python
if "name" in update_dict and update_dict["name"] != existing.name:
    duplicate = await repo.get_by_name(update_dict["name"])
    if duplicate:
        raise HTTPException(status_code=409, detail=f"Model with name '{update_dict['name']}' already exists")
```

**Why the conditions?**

- **Only check if name is being updated**: No need to query database if name unchanged
- **Exclude current model**: Updating without changing name shouldn't fail
- **Prevent duplicates**: Ensures unique constraint before database rejects it

### 4. Applying Updates

```python
for field, value in update_dict.items():
    setattr(existing, field, value)
```

**What's happening:**

- `setattr(obj, "field", value)` is same as `obj.field = value`
- Loops through all fields in update dictionary
- Updates only the fields provided in request
- Preserves unchanged fields

**Alternative approach:**

```python
# SQLAlchemy's update() method (more advanced)
from sqlalchemy import update

stmt = update(Model).where(Model.id == model_id).values(**update_dict)
await session.execute(stmt)
```

### Test the Update Endpoint

**Update a model:**

```bash
# Partial update (only description)
curl -X PATCH http://localhost:8000/api/v1/models/1 \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Updated: Most capable GPT-4 model with extended context"
  }'
```

**Expected response (200 OK):**

```json
{
  "id": 1,
  "name": "gpt-4-test",
  "display_name": "GPT-4 Test",
  "organization": "OpenAI",
  "release_date": "2023-03-14",
  "description": "Updated: Most capable GPT-4 model with extended context",
  "license": "Proprietary",
  "metadata_": null,
  "created_at": "2025-01-15T10:30:00",
  "updated_at": "2025-01-15T10:35:00"
}
```

**Notice:** Only `description` and `updated_at` changed!

**Try updating non-existent model:**

```bash
curl -X PATCH http://localhost:8000/api/v1/models/9999 \
  -H "Content-Type: application/json" \
  -d '{"description": "Test"}'
```

**Expected response (404 Not Found):**

```json
{
  "detail": "Model with id 9999 not found"
}
```

**🎯 Checkpoint:** You can update models with partial updates and proper validation!

---

## Step 3: Implementing DELETE - Removing Resources

Let's add the ability to delete resources.

### Understanding Delete Operations

**Two approaches:**

1. **Hard delete**: Permanently remove from database
2. **Soft delete**: Mark as deleted (add `is_deleted` field)

**We'll use hard delete** for this project. Soft delete is useful when you need:

- Audit trails
- Ability to restore deleted items
- Historical reporting

### Add Delete Endpoint

Add to `backend/app/api/v1/models.py`:

```python
@router.delete("/{model_id}", status_code=204)
async def delete_model(
    model_id: int,
    session: AsyncSession = Depends(get_db),
):
    """
    Delete an AI model by ID.

    This is a hard delete - the model and all related records (benchmark results,
    opinions, use cases) will be permanently removed due to cascade delete.

    Args:
        model_id: The unique identifier of the model to delete

    Returns:
        No content (204 status code)

    Raises:
        HTTPException 404: If model with given ID doesn't exist
        HTTPException 409: If model cannot be deleted due to constraints
    """
    repo = ModelRepository(session)

    # Check if model exists
    existing = await repo.get_by_id(model_id)
    if not existing:
        raise HTTPException(
            status_code=404,
            detail=f"Model with id {model_id} not found"
        )

    try:
        await repo.delete(model_id)
        # Return None with 204 No Content status
        return None
    except Exception as e:
        # If delete fails due to foreign key constraints or other issues
        raise HTTPException(
            status_code=409,
            detail=f"Cannot delete model: {str(e)}"
        )
```

**Key patterns in delete operations:**

### 1. Status Code 204 No Content

```python
@router.delete("/{model_id}", status_code=204)
async def delete_model(...):
    await repo.delete(model_id)
    return None  # No response body with 204
```

**Why 204?**

- Standard for successful DELETE operations
- Signals "successfully processed, no response body"
- Client knows operation succeeded without parsing response

**Alternative: 200 OK with response body**

```python
@router.delete("/{model_id}", response_model=ModelResponse)
async def delete_model(...):
    deleted_model = await repo.get_by_id(model_id)
    await repo.delete(model_id)
    return deleted_model  # Return what was deleted
```

Use this when clients need to know what was deleted (for undo functionality).

### 2. Cascade Delete Behavior

```python
# In your Model definition (from Module 1.1)
benchmark_results: list["BenchmarkResult"] = Relationship(
    back_populates="model",
    sa_relationship_kwargs={"cascade": "all, delete-orphan"}
)
```

**What happens when you delete a model?**

1. Model is deleted
2. All related `BenchmarkResult` records are deleted (cascade)
3. All related `Opinion` records are deleted (cascade)
4. All related `UseCase` records are deleted (cascade)

**Why cascade delete?**

- **Maintains referential integrity**: No orphaned records
- **Simplifies cleanup**: Don't need to manually delete related records
- **Prevents errors**: Foreign key constraints stay satisfied

**When NOT to use cascade delete:**

- **Shared resources**: Benchmarks are shared across models (no cascade)
- **Historical data**: Keep opinions even if model deleted (use soft delete)
- **Audit requirements**: Need to track what was deleted

### 3. Error Handling for Constraints

```python
except Exception as e:
    raise HTTPException(
        status_code=409,
        detail=f"Cannot delete model: {str(e)}"
    )
```

**When would delete fail?**

- **Foreign key constraint**: If cascade isn't configured and related records exist
- **Database lock**: Another transaction is using this record
- **Application constraint**: Custom business rule prevents deletion

**409 Conflict is appropriate** when the resource exists but cannot be deleted due to current state.

### Test the Delete Endpoint

**Delete a model:**

```bash
curl -X DELETE http://localhost:8000/api/v1/models/1
```

**Expected response (204 No Content):**

```
# Empty response body
# Check status code: should be 204
```

**Verify it's deleted:**

```bash
curl http://localhost:8000/api/v1/models/1
```

**Expected response (404 Not Found):**

```json
{
  "detail": "Model with id 1 not found"
}
```

**Try deleting non-existent model:**

```bash
curl -X DELETE http://localhost:8000/api/v1/models/9999
```

**Expected response (404 Not Found):**

```json
{
  "detail": "Model with id 9999 not found"
}
```

**🎯 Checkpoint:** You can delete models with proper error handling and cascade behavior!

---

## Step 4: Implementing Benchmarks CRUD

Now let's apply the same patterns to the Benchmarks resource. This reinforces the concepts and shows how consistent your API becomes.

### Add Benchmarks CRUD Operations

Update `backend/app/api/v1/benchmarks.py`:

```python
# Add to imports
from app.models.models import Benchmark, BenchmarkCreate, BenchmarkUpdate, BenchmarkResponse
from app.db.repositories import BenchmarkRepository

# Add after the existing endpoints

@router.post("/", response_model=BenchmarkResponse, status_code=201)
async def create_benchmark(
    benchmark_data: BenchmarkCreate,
    session: AsyncSession = Depends(get_db),
) -> BenchmarkResponse:
    """
    Create a new benchmark.

    Validates that no duplicate benchmark names exist before creation.
    """
    repo = BenchmarkRepository(session)

    # Check for duplicate name
    existing = await repo.get_by_name(benchmark_data.name)
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"Benchmark with name '{benchmark_data.name}' already exists"
        )

    try:
        new_benchmark = Benchmark(**benchmark_data.model_dump())
        created = await repo.create(new_benchmark)
        return created
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create benchmark: {str(e)}"
        )


@router.patch("/{benchmark_id}", response_model=BenchmarkResponse)
async def update_benchmark(
    benchmark_id: int,
    benchmark_data: BenchmarkUpdate,
    session: AsyncSession = Depends(get_db),
) -> BenchmarkResponse:
    """
    Update an existing benchmark (partial update).
    """
    repo = BenchmarkRepository(session)

    # Check if benchmark exists
    existing = await repo.get_by_id(benchmark_id)
    if not existing:
        raise HTTPException(
            status_code=404,
            detail=f"Benchmark with id {benchmark_id} not found"
        )

    # If updating name, check for duplicates
    update_dict = benchmark_data.model_dump(exclude_unset=True)
    if "name" in update_dict and update_dict["name"] != existing.name:
        duplicate = await repo.get_by_name(update_dict["name"])
        if duplicate:
            raise HTTPException(
                status_code=409,
                detail=f"Benchmark with name '{update_dict['name']}' already exists"
            )

    # Apply updates
    for field, value in update_dict.items():
        setattr(existing, field, value)

    try:
        updated = await repo.update(existing)
        return updated
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update benchmark: {str(e)}"
        )


@router.delete("/{benchmark_id}", status_code=204)
async def delete_benchmark(
    benchmark_id: int,
    session: AsyncSession = Depends(get_db),
):
    """
    Delete a benchmark by ID.

    Note: This will also delete all associated benchmark results due to cascade delete.
    """
    repo = BenchmarkRepository(session)

    # Check if benchmark exists
    existing = await repo.get_by_id(benchmark_id)
    if not existing:
        raise HTTPException(
            status_code=404,
            detail=f"Benchmark with id {benchmark_id} not found"
        )

    try:
        await repo.delete(benchmark_id)
        return None
    except Exception as e:
        raise HTTPException(
            status_code=409,
            detail=f"Cannot delete benchmark: {str(e)}"
        )
```

**Notice the pattern?** The code is nearly identical to Models CRUD:

1. **Check for existence** (404 if not found)
2. **Validate constraints** (409 if duplicate/conflict)
3. **Perform operation** via repository
4. **Handle errors** gracefully (500 if unexpected)
5. **Return appropriate status** (201, 200, 204)

**This consistency makes your API:**

- **Predictable**: Developers know what to expect
- **Maintainable**: Same patterns everywhere
- **Testable**: Same test structure for all resources
- **Documented**: Swagger UI shows same structure

**🎯 Checkpoint:** Benchmarks now have full CRUD operations following the same patterns as Models!

---

## Step 5: Implementing BenchmarkResults CRUD

BenchmarkResults are more complex because they're a **join table with extra data**. They connect Models to Benchmarks while storing the score.

### Understanding BenchmarkResults Constraints

Recall from Module 1.1:

```python
class BenchmarkResult(BenchmarkResultBase, TimestampMixin, table=True):
    model_id: int = Field(foreign_key="models.id", index=True)
    benchmark_id: int = Field(foreign_key="benchmarks.id", index=True)

    __table_args__ = (
        # Prevent duplicate results for same model+benchmark on same date
        UniqueConstraint("model_id", "benchmark_id", "date_tested", name="uix_model_benchmark_date"),
    )
```

**Validation requirements:**

1. **Model must exist** (foreign key constraint)
2. **Benchmark must exist** (foreign key constraint)
3. **No duplicates** for same model+benchmark+date
4. **Score must be valid** (Pydantic validation)

### Create BenchmarkResults Router

Create `backend/app/api/v1/benchmark_results.py`:

```python
"""
Benchmark Results API Router

Provides REST endpoints for managing model performance on benchmarks.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Sequence

from app.db import get_db
from app.db.repositories import BenchmarkResultRepository, ModelRepository, BenchmarkRepository
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
    limit: int = Query(default=20, le=100),
    model_id: int | None = Query(default=None, description="Filter by model ID"),
    benchmark_id: int | None = Query(default=None, description="Filter by benchmark ID"),
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
            status_code=404,
            detail=f"Benchmark result with id {result_id} not found"
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
            status_code=404,
            detail=f"Model with id {result_data.model_id} not found"
        )

    # Validate benchmark exists
    benchmark_repo = BenchmarkRepository(session)
    benchmark = await benchmark_repo.get_by_id(result_data.benchmark_id)
    if not benchmark:
        raise HTTPException(
            status_code=404,
            detail=f"Benchmark with id {result_data.benchmark_id} not found"
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
                )
            )

    try:
        new_result = BenchmarkResult(**result_data.model_dump())
        created = await result_repo.create(new_result)
        return created
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create benchmark result: {str(e)}"
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
            status_code=404,
            detail=f"Benchmark result with id {result_id} not found"
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
            status_code=500,
            detail=f"Failed to update benchmark result: {str(e)}"
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
            status_code=404,
            detail=f"Benchmark result with id {result_id} not found"
        )

    try:
        await repo.delete(result_id)
        return None
    except Exception as e:
        raise HTTPException(
            status_code=409,
            detail=f"Cannot delete benchmark result: {str(e)}"
        )
```

**Key differences from Models/Benchmarks CRUD:**

### 1. Reference Validation

```python
# Validate model exists
model = await model_repo.get_by_id(result_data.model_id)
if not model:
    raise HTTPException(status_code=404, detail=f"Model with id {result_data.model_id} not found")

# Validate benchmark exists
benchmark = await benchmark_repo.get_by_id(result_data.benchmark_id)
if not benchmark:
    raise HTTPException(status_code=404, detail=f"Benchmark with id {result_data.benchmark_id} not found")
```

**Why validate references?**

- **Better error messages**: "Model not found" vs "Foreign key violation"
- **404 instead of 500**: Proper HTTP semantics
- **Early validation**: Fails before attempting database insert
- **User-friendly**: Tells users exactly which reference is invalid

### 2. Composite Duplicate Checking

```python
exists = await result_repo.result_exists(
    model_id=result_data.model_id,
    benchmark_id=result_data.benchmark_id,
    date_tested=result_data.date_tested
)
if exists:
    raise HTTPException(status_code=409, detail="Result already exists")
```

**Why check three fields?**

- Matches the unique constraint: `(model_id, benchmark_id, date_tested)`
- Allows multiple results for same model+benchmark (different dates)
- Prevents accidental duplicates

### 3. Filtered Listing

```python
if model_id and benchmark_id:
    results = await repo.get_by_model_and_benchmark(...)
elif model_id:
    results = await repo.get_by_model_id(...)
elif benchmark_id:
    results = await repo.get_by_benchmark_id(...)
else:
    results = await repo.get_all(...)
```

**Enables flexible queries:**

```bash
# All results
GET /api/v1/benchmark-results/

# All results for GPT-4
GET /api/v1/benchmark-results/?model_id=1

# All results for MMLU benchmark
GET /api/v1/benchmark-results/?benchmark_id=5

# GPT-4's results on MMLU
GET /api/v1/benchmark-results/?model_id=1&benchmark_id=5
```

### Include the Router

Update `backend/app/api/v1/__init__.py`:

```python
from . import models, benchmarks, benchmark_results

__all__ = ["models", "benchmarks", "benchmark_results"]
```

Update `backend/app/main.py`:

```python
from app.api.v1 import models, benchmarks, benchmark_results

# Include all routers
app.include_router(models.router)
app.include_router(benchmarks.router)
app.include_router(benchmark_results.router)
```

**🎯 Checkpoint:** BenchmarkResults have full CRUD with reference validation and composite constraints!

---

## Step 6: Implementing Related Resource Endpoints

Often you want to access related resources through a parent. For example: "Get all benchmark results for model 5".

**Two approaches:**

1. **Query parameters**: `GET /api/v1/benchmark-results/?model_id=5`
2. **Nested routes**: `GET /api/v1/models/5/benchmarks`

**Both are valid!** Let's implement nested routes for common relationships.

### Add Related Benchmarks Endpoint

Add to `backend/app/api/v1/models.py`:

```python
from app.models.models import BenchmarkResultResponse

# Add after the delete endpoint

@router.get("/{model_id}/benchmarks", response_model=list[BenchmarkResultResponse])
async def get_model_benchmarks(
    model_id: int,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, le=100),
    session: AsyncSession = Depends(get_db),
) -> Sequence[BenchmarkResultResponse]:
    """
    Get all benchmark results for a specific model.

    Returns the model's performance on all benchmarks it has been tested on.
    """
    # First check if model exists
    model_repo = ModelRepository(session)
    model = await model_repo.get_by_id(model_id)
    if not model:
        raise HTTPException(
            status_code=404,
            detail=f"Model with id {model_id} not found"
        )

    # Get benchmark results for this model
    from app.db.repositories import BenchmarkResultRepository
    result_repo = BenchmarkResultRepository(session)
    results = await result_repo.get_by_model_id(model_id, skip=skip, limit=limit)

    return results
```

**Why nested routes?**

- **Intuitive**: `/models/5/benchmarks` clearly shows relationship
- **Resource-oriented**: Models "have" benchmark results
- **Self-documenting**: API structure mirrors data relationships
- **RESTful**: Follows REST conventions for hierarchical resources

**When to use nested vs flat?**

```python
# Nested (when relationship is strong)
GET /api/v1/models/5/benchmarks        # "This model's benchmarks"
GET /api/v1/models/5/opinions          # "This model's opinions"

# Flat with filters (when filtering across multiple dimensions)
GET /api/v1/benchmark-results/?model_id=5&benchmark_id=3
```

### Add More Related Endpoints

Add to `backend/app/api/v1/benchmarks.py`:

```python
from app.models.models import BenchmarkResultResponse

@router.get("/{benchmark_id}/results", response_model=list[BenchmarkResultResponse])
async def get_benchmark_results(
    benchmark_id: int,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, le=100),
    session: AsyncSession = Depends(get_db),
) -> Sequence[BenchmarkResultResponse]:
    """
    Get all results for a specific benchmark across all models.

    Useful for comparing how different models perform on the same benchmark.
    """
    # Check if benchmark exists
    repo = BenchmarkRepository(session)
    benchmark = await repo.get_by_id(benchmark_id)
    if not benchmark:
        raise HTTPException(
            status_code=404,
            detail=f"Benchmark with id {benchmark_id} not found"
        )

    # Get results for this benchmark
    from app.db.repositories import BenchmarkResultRepository
    result_repo = BenchmarkResultRepository(session)
    results = await result_repo.get_by_benchmark_id(benchmark_id, skip=skip, limit=limit)

    return results
```

**Now you can query:**

```bash
# All benchmark results for GPT-4
GET /api/v1/models/5/benchmarks

# All models' results on MMLU
GET /api/v1/benchmarks/3/results
```

**🎯 Checkpoint:** You have related resource endpoints that make querying relationships easy!

---

## Step 7: Adding Search Functionality

Let's implement search endpoints using the repository search methods from Module 1.2.

### Add Model Search Endpoint

Add to `backend/app/api/v1/models.py`:

```python
@router.get("/search/", response_model=list[ModelResponse])
async def search_models(
    q: str = Query(..., min_length=2, description="Search query (minimum 2 characters)"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, le=100),
    session: AsyncSession = Depends(get_db),
) -> Sequence[ModelResponse]:
    """
    Search for models by name or organization.

    The search is case-insensitive and matches partial strings.
    Searches across name and organization fields.

    Args:
        q: Search query (minimum 2 characters)
        skip: Pagination offset
        limit: Maximum results

    Returns:
        List of models matching the search query

    Examples:
        /api/v1/models/search/?q=gpt       # Find all GPT models
        /api/v1/models/search/?q=openai    # Find all OpenAI models
        /api/v1/models/search/?q=coding    # Find models mentioning coding
    """
    repo = ModelRepository(session)
    results = await repo.search(query=q, skip=skip, limit=limit)
    return results
```

**Key search patterns:**

### 1. Query Parameter Validation

```python
q: str = Query(..., min_length=2, description="Search query (minimum 2 characters)")
```

**What `...` means:**

- Required parameter (no default value)
- Request fails with 422 if missing
- Alternative: `Query(default=None)` for optional

**Why minimum length?**

- Short queries are too broad ("a" matches everything)
- Performance: Prevents expensive full-table scans
- User experience: Encourages specific searches

### 2. URL Path Considerations

```python
@router.get("/search/", response_model=list[ModelResponse])
```

**Why `/search/` instead of `/models/search`?**

The router already has prefix `/api/v1/models`, so:

```python
@router.get("/search/")  # → /api/v1/models/search/
@router.get("/{model_id}")  # → /api/v1/models/{model_id}
```

**Important: Order matters!**

```python
# ✅ Correct order
@router.get("/search/")       # Specific route first
@router.get("/{model_id}")    # Parameterized route second

# ❌ Wrong order (FastAPI matches first route)
@router.get("/{model_id}")    # Catches "/search" as model_id!
@router.get("/search/")       # Never reached
```

**Solution:** Put specific routes before parameterized routes.

### Test Search

```bash
# Search for GPT models
curl "http://localhost:8000/api/v1/models/search/?q=gpt"

# Search for OpenAI models
curl "http://localhost:8000/api/v1/models/search/?q=openai"

# Search with pagination
curl "http://localhost:8000/api/v1/models/search/?q=model&limit=5"

# Try too short (should fail with 422)
curl "http://localhost:8000/api/v1/models/search/?q=a"
```

**🎯 Checkpoint:** You have search functionality with validation and pagination!

---

## Step 8: Writing Minimal CRUD Tests (Models Only)

We're keeping tests focused and lightweight so you can move quickly. We'll test
only the Models resource and cover the core create/update/delete flows.

### Create a Small CRUD Test File

Create `backend/tests/api/test_models_crud.py`:

```python
"""
Tests for Models CRUD operations

Keeps a small set of unit tests for core CRUD behavior.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from datetime import date

from app.models.models import Model


@pytest.mark.unit
class TestModelsCRUDUnit:
    """Unit tests for Models CRUD with mocked repository"""

    @patch("app.api.v1.models.ModelRepository")
    def test_create_model_success(self, MockRepo: AsyncMock, client: TestClient):
        """Test creating a new model successfully"""
        # Setup mock
        mock_repo_instance = AsyncMock()
        mock_repo_instance.get_by_name.return_value = None  # No duplicate

        created_model = Model(
            id=1,
            name="test-model",
            display_name="Test Model",
            organization="Test Org",
            release_date=date(2025, 1, 1),
            created_at=date(2025, 1, 2)
        )
        mock_repo_instance.create.return_value = created_model
        MockRepo.return_value = mock_repo_instance

        # Make request
        response = client.post(
            "/api/v1/models/",
            json={
                "name": "test-model",
                "display_name": "Test Model",
                "organization": "Test Org",
                "release_date": "2024-01-01"
            }
        )

        # Assertions
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "test-model"
        assert data["id"] == 1
        mock_repo_instance.get_by_name.assert_awaited_once_with("test-model")
        mock_repo_instance.create.assert_awaited_once()

    @patch("app.api.v1.models.ModelRepository")
    def test_update_model_success(self, MockRepo: AsyncMock, client: TestClient):
        """Test updating a model successfully"""
        # Setup mock
        mock_repo_instance = AsyncMock()

        existing_model = Model(
            id=1,
            name="old-name",
            display_name="Old Display",
            organization="Test"
        )
        mock_repo_instance.get_by_id.return_value = existing_model

        updated_model = Model(
            id=1,
            name="old-name",
            display_name="New Display",
            organization="Test"
        )
        mock_repo_instance.update.return_value = updated_model
        MockRepo.return_value = mock_repo_instance

        # Make request
        response = client.patch(
            "/api/v1/models/1",
            json={"display_name": "New Display"}
        )

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["display_name"] == "New Display"
        mock_repo_instance.get_by_id.assert_awaited_once_with(1)
        mock_repo_instance.update.assert_awaited_once()

    @patch("app.api.v1.models.ModelRepository")
    def test_delete_model_success(self, MockRepo: AsyncMock, client: TestClient):
        """Test deleting a model successfully"""
        # Setup mock
        mock_repo_instance = AsyncMock()
        existing_model = Model(id=1, name="test", display_name="Test", organization="Test")
        mock_repo_instance.get_by_id.return_value = existing_model
        mock_repo_instance.delete.return_value = True
        MockRepo.return_value = mock_repo_instance

        # Make request
        response = client.delete("/api/v1/models/1")

        # Assertions
        assert response.status_code == 204
        assert response.content == b""
        mock_repo_instance.get_by_id.assert_awaited_once_with(1)
        mock_repo_instance.delete.assert_awaited_once_with(1)

```

### Run CRUD Tests

```bash
cd backend

# Run all CRUD tests
uv run pytest tests/api/test_models_crud.py -v

# Run only unit tests
uv run pytest tests/api/test_models_crud.py -m unit -v
```

**🎯 Checkpoint:** You have lightweight CRUD tests for the Models resource!

---

## Understanding Transaction Management

One advanced topic worth understanding: **when do database changes commit?**

### How Transactions Work in Your API

**Request lifecycle:**

1. **Request arrives** → `get_db()` creates session
2. **Endpoint executes** → Calls repository methods
3. **Repository commits** → `await session.commit()` in create/update/delete
4. **Request completes** → `get_db()` closes session

**Key points:**

```python
# In BaseRepository.create()
async def create(self, entity: ModelType) -> ModelType:
    self.session.add(entity)
    await self.session.commit()  # ← Commits here
    await self.session.refresh(entity)
    return entity
```

**Each repository method commits independently.** This is fine for simple operations but can be problematic for complex workflows.

### Problem: Multi-Step Operations

```python
@router.post("/bulk-import")
async def import_models(models: list[ModelCreate], session: AsyncSession = Depends(get_db)):
    """Import multiple models - all or nothing"""
    repo = ModelRepository(session)

    for model_data in models:
        new_model = Model(**model_data.model_dump())
        await repo.create(new_model)  # Commits immediately!

    # If error occurs here, some models are already committed!
    # Can't roll back previous creates
```

**The issue:**

- 5 models imported successfully
- 6th model fails (duplicate name)
- First 5 are already in database
- **Partial import** instead of all-or-nothing

### Solution: Transaction Management

**Option 1: Don't commit in repository (advanced pattern)**

```python
async def create_no_commit(self, entity: ModelType) -> ModelType:
    """Create entity without committing"""
    self.session.add(entity)
    await self.session.flush()  # Validates but doesn't commit
    return entity

@router.post("/bulk-import")
async def import_models(models: list[ModelCreate], session: AsyncSession = Depends(get_db)):
    repo = ModelRepository(session)

    try:
        for model_data in models:
            new_model = Model(**model_data.model_dump())
            await repo.create_no_commit(new_model)

        # All succeeded, commit once
        await session.commit()
    except Exception:
        # Any failure, rollback all
        await session.rollback()
        raise
```

**Option 2: Use nested transactions (savepoints)**

```python
@router.post("/bulk-import")
async def import_models(models: list[ModelCreate], session: AsyncSession = Depends(get_db)):
    repo = ModelRepository(session)

    async with session.begin_nested():  # Savepoint
        for model_data in models:
            new_model = Model(**model_data.model_dump())
            await repo.create(new_model)
        # Auto-commits or rolls back the savepoint
```

**For this course:** Our current approach (commit per operation) is fine for simple CRUD. For complex workflows, use transactions.

**🎯 Checkpoint:** You understand transaction management for complex operations!

## What You've Accomplished

Congratulations! You've built a **production-quality CRUD API**. Here's what you now have:

### 1. Complete CRUD Operations

- ✅ **Create (POST)** with duplicate checking and validation
- ✅ **Read (GET)** with filtering and pagination
- ✅ **Update (PATCH)** with partial updates and constraint checking
- ✅ **Delete (DELETE)** with cascade behavior
- ✅ **Search** with query-based filtering

### 2. Professional Error Handling

- ✅ **Proper HTTP status codes** for all scenarios
- ✅ **User-friendly messages** that guide clients
- ✅ **Consistent error responses** across CRUD endpoints

### 3. Input Validation

- ✅ **Schema validation** via Pydantic (automatic)
- ✅ **Duplicate checking** before creation
- ✅ **Reference validation** (foreign keys exist)
- ✅ **Constraint checking** (unique constraints)

### 4. Related Resources

- ✅ **Nested endpoints** (`/models/{id}/benchmarks`)
- ✅ **Filtered queries** (`?model_id=5`)
- ✅ **Eager loading** for relationships

### 5. Focused Testing

- ✅ **Unit tests** with mocked repositories (fast)
- ✅ **CRUD test coverage** for Models (core resource)
- ✅ **Happy-path testing** for create/update/delete

### 6. REST Best Practices

- ✅ **Resource-oriented URLs** (`/models`, `/benchmarks`)
- ✅ **Proper HTTP methods** (GET, POST, PATCH, DELETE)
- ✅ **Correct status codes** (200, 201, 204, 404, 409)
- ✅ **Consistent response format** across all endpoints

---

## Key Takeaways

**On CRUD Operations:**

- **POST creates, PATCH updates, DELETE removes** - each with proper status codes
- **Check before you create/update/delete** - validate constraints before database operations
- **Duplicate checking is essential** - return 409 Conflict for duplicates
- **Reference validation matters** - verify foreign keys exist before creating relationships

**On Error Handling:**

- **Status codes communicate outcomes** - 404 not found, 409 conflict, 422 validation
- **User-friendly messages guide users** - tell them what went wrong and how to fix it
- **Keep error formats consistent** - make API usage predictable
- **Don’t expose raw errors to clients** - log details server-side, return generic messages

**On Validation:**

- **Schemas validate automatically** - Pydantic checks types and constraints
- **Business rules need explicit checks** - uniqueness, references, state transitions
- **exclude_unset enables partial updates** - only update fields actually provided
- **Validate early, fail fast** - check before expensive operations

**On Testing:**

- **Unit tests are fast** - mock repositories for HTTP layer testing
- **Start with core flows** - create, update, delete on Models
- **Expand later** - add more resources and error cases after the basics

**On Architecture:**

- **Consistency makes APIs predictable** - same patterns for all resources
- **Separation of concerns is powerful** - API layer validates, repository layer persists
- **Error handling is a feature** - good errors make your API better
- **Transaction management matters** - understand when changes commit

---

## What's Next?

In **Module 3.1: LLM Integration Basics**, you'll:

- **Integrate Claude API** for intelligent data extraction
- **Build prompt templates** for structured output
- **Handle LLM responses** with validation and retry logic
- **Cache LLM results** to save costs during development
- **Extract structured data** from unstructured text
- **Test LLM integrations** with mocked responses

You've mastered the API layer. Now it's time to add AI-powered features that make your application truly intelligent!

---

## Hands-On Exercises

Before moving to the next module, solidify your learning:

### Exercise 1: Complete Opinions CRUD

Implement full CRUD operations for the Opinions resource:

**Requirements:**

- Create `backend/app/api/v1/opinions.py`
- POST, GET, PATCH, DELETE endpoints
- Validate that model_id exists before creating opinion
- Filter opinions by model_id, sentiment, or date range
- Add search by content (full-text search)
- Basic unit tests for create/update/delete

**Acceptance Criteria:**

- All endpoints return proper status codes
- Duplicate checking where applicable
- Reference validation (model exists)
- Tests cover create, update, delete, and filtering

### Exercise 2: Add UseCases CRUD

Implement full CRUD for UseCases:

**Requirements:**

- Create `backend/app/api/v1/use_cases.py`
- Full CRUD endpoints
- Validate model_id exists
- Group use cases by model
- Search use cases by description

**Acceptance Criteria:**

- Follows same patterns as Models/Benchmarks
- Proper error handling
- Tests for all operations

### Exercise 3: Implement Bulk Operations

Add bulk creation endpoint:

**Requirements:**

- `POST /api/v1/models/bulk` accepts array of ModelCreate
- All-or-nothing transaction (all succeed or all fail)
- Return summary of created models
- Handle partial failures gracefully

**Acceptance Criteria:**

- Uses transaction management
- Validates all models before creating any
- Returns 207 Multi-Status with detailed results
- Tests verify transaction rollback on failure

### Exercise 4: Add Soft Delete

Implement soft delete for Models:

**Requirements:**

- Add `is_deleted` boolean field to Model
- `DELETE /models/{id}` sets is_deleted=True
- `GET /models` excludes soft-deleted by default
- Add `?include_deleted=true` query parameter
- Add `POST /models/{id}/restore` to un-delete

**Acceptance Criteria:**

- Soft-deleted models don't appear in list
- Can still get by ID to see deleted status
- Restore endpoint works correctly
- Tests verify soft delete behavior

### Exercise 5: Add Filtering and Sorting

Enhance the list endpoints:

**Requirements:**

- Add filtering: `?organization=OpenAI&license=MIT`
- Add sorting: `?sort_by=release_date&order=desc`
- Add date range: `?from_date=2024-01-01&to_date=2024-12-31`
- Combine multiple filters

**Acceptance Criteria:**

- Filters work individually and combined
- Sorting supports multiple fields
- Date range filtering works correctly
- Tests verify all filter combinations

---

## Additional Resources

### FastAPI Advanced Topics

- [Request Body Validation](https://fastapi.tiangolo.com/tutorial/body-updates/)
- [Custom Response Models](https://fastapi.tiangolo.com/advanced/response-model/)
- [Exception Handling](https://fastapi.tiangolo.com/tutorial/handling-errors/)
- [Background Tasks](https://fastapi.tiangolo.com/tutorial/background-tasks/)

### REST API Design

- [REST API Best Practices](https://stackoverflow.blog/2020/03/02/best-practices-for-rest-api-design/)
- [HTTP Status Codes Guide](https://www.restapitutorial.com/httpstatuscodes.html)
- [API Error Handling](https://nordicapis.com/best-practices-api-error-handling/)

### Database Transactions

- [SQLAlchemy Session Basics](https://docs.sqlalchemy.org/en/20/orm/session_basics.html)
- [Understanding Database Transactions](https://www.postgresql.org/docs/current/tutorial-transactions.html)
- [Async SQLAlchemy](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)

### Testing

- [pytest Fixtures](https://docs.pytest.org/en/stable/fixture.html)
- [Mocking with unittest.mock](https://docs.python.org/3/library/unittest.mock.html)
- [Integration Testing Strategies](https://testdriven.io/blog/fastapi-crud/)

---

**Congratulations!** You've built a production-quality CRUD API with comprehensive error handling, validation, and testing. You're ready to add AI-powered features in Module 3!
