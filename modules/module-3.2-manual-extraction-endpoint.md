# Module 3.2: Manual Extraction Endpoint - Connecting LLM to Database

**Duration:** 3-4 hours
**Difficulty:** Intermediate-Advanced
**Prerequisites:** Module 3.1 (LLM Integration Basics) complete

---

## Overview

In Module 3.1, you built an `LLMService` that can read arbitrary text and extract structured AI model data using Claude. You've got the extraction working, returning clean `ExtractionResult` objects with validated data. That's a huge achievement!

But here's the exciting part: **you haven't actually created any database records yet**. Your LLM service is currently isolated - it extracts data beautifully, but doesn't connect to your Model Catalogue database.

**In this module, you'll bridge that gap.** You'll create a `/api/v1/extract` endpoint that:

1. Accepts arbitrary text from users
2. Uses your `LLMService` to extract model data
3. Validates the extracted data against your database schemas
4. Checks for duplicate models
5. Creates the model in your database via the repository layer
6. Returns the created model with proper HTTP status codes

This completes your **manual extraction pipeline** - the first of two data ingestion methods (the second being automated RSS processing in Module 4).

**The journey of a text snippet:**

```
User input text
      ↓
POST /api/v1/extract
      ↓
LLMService.extract_model_data()
      ↓
Validate against ModelCreate schema
      ↓
Check for duplicates (ModelRepository)
      ↓
Create in database (ModelRepository)
      ↓
Return ModelResponse (201 Created)
```

By the end, you'll have a production-ready endpoint that lets users paste text about any AI model and automatically populate your catalogue. This is the foundation for building an AI-powered data entry system.

## Learning Objectives

By the end of this module, you will be able to:

1. **Create API endpoints that orchestrate multiple services** (LLM + Repository pattern)
2. **Implement FastAPI dependency injection** for service classes
3. **Validate LLM outputs** before database insertion using Pydantic schemas
4. **Handle duplicate detection** with proper HTTP status codes (409 Conflict)
5. **Map between schema types** (ExtractedModel → ModelCreate → Model → ModelResponse)
6. **Design comprehensive error handling** for multi-step operations
7. **Write integration tests** that verify the entire extraction pipeline
8. **Document API endpoints** with clear examples and OpenAPI metadata

## Prerequisites

Before starting, ensure you have:

- Completed Module 3.1 (LLMService implementation)
- Working repository layer (Module 1.2)
- CRUD API endpoints (Module 2.2)
- Understanding of FastAPI dependency injection
- Anthropic API key configured in `.env`

**Quick verification:**

```bash
# Test your LLM service works
cd backend
uv run pytest tests/test_llm_service.py::TestModelExtraction -v

# Verify repository layer
uv run pytest tests/test_repositories.py -v
```

If both pass, you're ready to proceed!

---

## Conceptual Foundation

### The Problem: LLM Outputs Need Validation

Your `LLMService` returns an `ExtractionResult` with extracted data. But consider these scenarios:

**Scenario 1: Duplicate model**
```python
# User pastes: "GPT-4 was released by OpenAI..."
# LLM extracts: model_name="gpt-4"
# Problem: gpt-4 already exists in database!
```

**Scenario 2: Invalid data**
```python
# User pastes: "Some random text about dogs..."
# LLM extracts: model_name="dog-classifier", organization=None
# Problem: We need organization to be set, or handle missing fields
```

**Scenario 3: Schema mismatch**
```python
# LLM returns: release_date="March 2023" (string)
# Database expects: release_date=date(2023, 3, 1) (date object)
# LLMService already handles this - but what if format changes?
```

**The key insight:** LLM outputs are probabilistic. Even with structured outputs, you must validate before database insertion. Never trust AI outputs blindly.

### The Solution: Multi-Layer Validation

Your extraction endpoint needs **defense in depth**:

```python
# Layer 1: Pydantic schema validation (automatic with ExtractedModel)
extracted_data = llm_service.extract_model_data(text)

# Layer 2: Convert to database schema (ModelCreate)
model_create = ModelCreate(
    name=extracted_data.data.model_name,
    organization=extracted_data.data.organization,
    # ... map all fields
)

# Layer 3: Business validation (duplicate checking)
existing = await model_repo.get_by_name(model_create.name)
if existing:
    raise HTTPException(409, "Model already exists")

# Layer 4: Database constraints (foreign keys, NOT NULL, etc.)
created = await model_repo.create(Model(**model_create.model_dump()))
```

Each layer catches different error types:
- **Layer 1**: Type errors (string instead of date)
- **Layer 2**: Schema conformance (required fields)
- **Layer 3**: Business rules (no duplicates)
- **Layer 4**: Database integrity (constraints)

### Industry Context: Orchestration Endpoints

The `/extract` endpoint is an **orchestration endpoint** - it coordinates multiple services:

- **LLMService**: Handles AI extraction
- **ModelRepository**: Manages database operations
- **Validation**: Ensures data quality

This is a common pattern in production APIs:

```python
# E-commerce checkout (orchestrates multiple services)
@router.post("/checkout")
async def checkout(cart_id: int, payment: PaymentInfo):
    cart = await cart_service.get_cart(cart_id)
    await payment_service.charge(payment, cart.total)
    order = await order_service.create_order(cart)
    await email_service.send_confirmation(order)
    await inventory_service.decrement_stock(cart.items)
    return order

# Your extraction endpoint (orchestrates LLM + Repository)
@router.post("/extract")
async def extract_and_create(text: str):
    result = await llm_service.extract_model_data(text)
    model_create = convert_to_create_schema(result.data)
    await validate_no_duplicates(model_create.name)
    created = await model_repo.create(model_create)
    return created
```

**Key principle:** Endpoints handle HTTP concerns (request/response, status codes). Services handle business logic (extraction, validation, database operations).

### The Challenge: Error Handling at Scale

With multiple operations, errors can occur at any step. Your endpoint must handle:

1. **Empty text** → 400 Bad Request
2. **LLM extraction failure** → 500 Internal Server Error (with retry already in LLMService)
3. **No model found in text** → 400 Bad Request ("No model information found")
4. **Duplicate model** → 409 Conflict
5. **Invalid schema** → 422 Unprocessable Entity
6. **Database failure** → 500 Internal Server Error

Each error needs:
- Appropriate HTTP status code
- Clear error message for debugging
- Logging for monitoring
- Client-friendly response format

FastAPI's `HTTPException` makes this straightforward:

```python
if not result.data:
    raise HTTPException(
        status_code=400,
        detail="No model information could be extracted from the provided text"
    )
```

---

## Implementation Guide

### Step 1: Design the Request/Response Schemas

First, create schemas for the extraction endpoint. These are separate from your `Model` schemas because they serve a different purpose.

**Create a new file:** `backend/app/schemas/extraction.py`

```python
"""
Extraction API Schemas

Request/response models for the LLM-powered extraction endpoint.
These are separate from Model schemas because they include metadata
about the extraction process.
"""

from pydantic import BaseModel, Field
from app.models import ModelResponse


class ExtractRequest(BaseModel):
    """
    Request body for the extraction endpoint.

    Contains the raw text to extract model information from.
    """

    text: str = Field(
        ...,
        min_length=10,
        description="Text to extract model information from",
        examples=[
            "GPT-4 was released by OpenAI in March 2023. It's a large multimodal model."
        ]
    )


class ExtractResponse(BaseModel):
    """
    Response from the extraction endpoint.

    Contains the created model plus metadata about the extraction process
    (useful for monitoring token usage and debugging).
    """

    model: ModelResponse = Field(
        description="The created model entry"
    )

    tokens_used: int = Field(
        description="Number of tokens consumed by the LLM extraction"
    )

    llm_model: str = Field(
        description="Claude model used for extraction",
        examples=["claude-sonnet-4-5"]
    )


class ExtractErrorResponse(BaseModel):
    """
    Error response when extraction fails.

    Provides detailed information about what went wrong.
    """

    detail: str = Field(
        description="Human-readable error message"
    )

    error_type: str = Field(
        description="Error category for client handling",
        examples=["duplicate", "no_data_found", "extraction_failed", "validation_error"]
    )
```

**Why separate schemas?**

- `ExtractRequest`: Simple text input (different from `ModelCreate` which has all model fields)
- `ExtractResponse`: Includes extraction metadata (tokens, LLM model) that `ModelResponse` doesn't have
- `ExtractErrorResponse`: Structured errors with `error_type` for programmatic handling

**Update** `backend/app/schemas/__init__.py`:

```python
from .extraction import ExtractRequest, ExtractResponse, ExtractErrorResponse

__all__ = [
    # ... existing exports
    "ExtractRequest",
    "ExtractResponse",
    "ExtractErrorResponse",
]
```

### Step 2: Create a Service Dependency

You need to inject `LLMService` into your endpoint. FastAPI's dependency injection makes this clean and testable.

**Create** `backend/app/api/dependencies.py`:

```python
"""
FastAPI Dependencies

Provides dependency injection for services, database sessions,
and other shared resources.
"""

from typing import AsyncIterator
from app.services.llm_service import LLMService
from app.db import get_db
from sqlmodel.ext.asyncio.session import AsyncSession


# Database dependency (already exists in db/__init__.py, but good to have here)
async def get_db_session() -> AsyncIterator[AsyncSession]:
    """Provide database session to endpoints"""
    async for session in get_db():
        yield session


# LLM Service dependency (singleton pattern - reuse across requests)
_llm_service_instance: LLMService | None = None


def get_llm_service() -> LLMService:
    """
    Provide LLMService to endpoints.

    Uses singleton pattern to reuse the same service instance
    across requests (avoiding repeated client initialization).

    Returns:
        Initialized LLMService with API key from settings

    Raises:
        ValueError: If ANTHROPIC_API_KEY not configured
    """
    global _llm_service_instance

    if _llm_service_instance is None:
        _llm_service_instance = LLMService()

    return _llm_service_instance
```

**Why a singleton?**

Creating a new `LLMService` for each request is wasteful - the Anthropic client can be reused. The singleton pattern ensures one instance serves all requests.

**Alternative approach (factory pattern):**

```python
# If you need fresh instances per request (e.g., for different API keys)
async def get_llm_service() -> AsyncIterator[LLMService]:
    service = LLMService()
    try:
        yield service
    finally:
        await service.close()  # Clean up client
```

For this module, the singleton is simpler and more efficient.

### Step 3: Implement Helper Functions

Before building the endpoint, create helper functions for common operations. This keeps your endpoint clean and testable.

**Create** `backend/app/api/v1/extraction_helpers.py`:

```python
"""
Extraction Endpoint Helper Functions

Business logic for the extraction endpoint, separated for testability.
"""

from datetime import date
from app.services.llm_service import ExtractedModel
from app.models import ModelCreate


def convert_extracted_to_create(extracted: ExtractedModel) -> ModelCreate:
    """
    Convert LLM-extracted data to ModelCreate schema.

    Maps field names and ensures data types match the database schema.

    Args:
        extracted: Data extracted by LLMService

    Returns:
        ModelCreate schema ready for database insertion

    Example:
        extracted = ExtractedModel(model_name="gpt-4", ...)
        model_create = convert_extracted_to_create(extracted)
        # model_create.name == "gpt-4"  (field name changed)
    """
    return ModelCreate(
        name=extracted.model_name,  # Field name mapping!
        organization=extracted.organization,
        release_date=extracted.release_date,
        description=extracted.description,
        license=extracted.license,
    )


def validate_extracted_data(extracted: ExtractedModel | None) -> None:
    """
    Validate that extraction produced usable data.

    Raises HTTPException with appropriate status code if data is invalid.

    Args:
        extracted: Extracted model data (or None if extraction failed)

    Raises:
        HTTPException(400): If no data was extracted
        HTTPException(422): If required fields are missing
    """
    from fastapi import HTTPException

    if extracted is None:
        raise HTTPException(
            status_code=400,
            detail="No model information could be extracted from the provided text. "
                   "Please ensure the text contains information about an AI model."
        )

    # Validate required fields (model_name and description are required in ExtractedModel)
    # Pydantic already validates this, but we can add business logic here

    # Example: Require organization for production systems
    # if not extracted.organization:
    #     raise HTTPException(
    #         status_code=422,
    #         detail="Model organization is required but was not found in the text"
    #     )
```

**Why helper functions?**

1. **Testability**: Test `convert_extracted_to_create()` independently
2. **Reusability**: Use in other endpoints if needed
3. **Clarity**: Endpoint code stays focused on HTTP concerns
4. **Maintainability**: Change mapping logic in one place

### Step 4: Create the Extraction Router

Now create a new router for extraction-related endpoints.

**Create** `backend/app/api/v1/extraction.py`:

```python
"""
Extraction API Router

Provides endpoints for LLM-powered data extraction and insertion.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db import get_db
from app.db.repositories import ModelRepository
from app.services.llm_service import LLMService
from app.schemas.extraction import ExtractRequest, ExtractResponse
from app.models import Model
from app.api.dependencies import get_llm_service
from app.api.v1.extraction_helpers import (
    convert_extracted_to_create,
    validate_extracted_data,
)

import logging

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/api/v1",
    tags=["extraction"],
    responses={
        400: {"description": "Invalid request or no data found"},
        409: {"description": "Model already exists"},
        500: {"description": "Extraction or database error"},
    },
)


@router.post("/extract", response_model=ExtractResponse, status_code=201)
async def extract_and_create_model(
    request: ExtractRequest,
    llm_service: LLMService = Depends(get_llm_service),
    session: AsyncSession = Depends(get_db),
) -> ExtractResponse:
    """
    Extract AI model information from text and create database entry.

    This endpoint uses Claude to automatically parse unstructured text
    (research papers, blog posts, announcements) and extract model information.

    The extraction process:
    1. LLM reads the text and identifies model information
    2. Extracted data is validated against schemas
    3. System checks for duplicate models
    4. New model is created in the database
    5. Response includes the model and extraction metadata

    Args:
        request: Text containing model information
        llm_service: Injected LLMService instance
        session: Database session

    Returns:
        ExtractResponse with created model and token usage

    Raises:
        HTTPException(400): Empty text or no model information found
        HTTPException(409): Model with same name already exists
        HTTPException(500): LLM API error or database failure

    Example:
        POST /api/v1/extract
        {
            "text": "GPT-4 was released by OpenAI in March 2023..."
        }

        Response (201 Created):
        {
            "model": {
                "id": 1,
                "name": "gpt-4",
                "organization": "OpenAI",
                "release_date": "2023-03-01",
                ...
            },
            "tokens_used": 650,
            "llm_model": "claude-sonnet-4-5"
        }
    """

    logger.info(f"Extraction request received (text length: {len(request.text)} chars)")

    # Step 1: Extract data using LLM
    try:
        extraction_result = await llm_service.extract_model_data(
            text=request.text,
            use_cache=True  # Enable caching to reduce costs
        )
    except ValueError as e:
        # LLM service raises ValueError for empty text
        logger.error(f"Extraction validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Catch all other errors (API failures, network issues, etc.)
        logger.error(f"LLM extraction failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to extract data from text: {str(e)}"
        )

    logger.info(
        f"Extraction complete: {extraction_result.tokens_used} tokens, "
        f"model: {extraction_result.model_used}"
    )

    # Step 2: Validate extraction produced data
    validate_extracted_data(extraction_result.data)

    # Step 3: Convert to ModelCreate schema
    model_create = convert_extracted_to_create(extraction_result.data)

    logger.info(f"Extracted model: {model_create.name} by {model_create.organization}")

    # Step 4: Check for duplicate models
    repo = ModelRepository(session)
    existing_model = await repo.get_by_name(model_create.name)

    if existing_model:
        logger.warning(f"Duplicate model detected: {model_create.name} (id={existing_model.id})")
        raise HTTPException(
            status_code=409,
            detail=f"Model '{model_create.name}' already exists with ID {existing_model.id}. "
                   f"Use PATCH /api/v1/models/{existing_model.id} to update it."
        )

    # Step 5: Create model in database
    try:
        new_model = Model(**model_create.model_dump())
        created_model = await repo.create(new_model)
        logger.info(f"Model created successfully: {created_model.name} (id={created_model.id})")
    except Exception as e:
        logger.error(f"Database creation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create model in database: {str(e)}"
        )

    # Step 6: Build response with metadata
    return ExtractResponse(
        model=created_model,
        tokens_used=extraction_result.tokens_used,
        llm_model=extraction_result.model_used,
    )
```

**Code walkthrough:**

1. **Logging**: Track each step for debugging and monitoring
2. **Error handling**: Separate `ValueError` (client errors → 400) from other exceptions (server errors → 500)
3. **Helpful error messages**: Tell users exactly what went wrong and how to fix it
4. **Extraction metadata**: Return token usage so users can monitor costs
5. **Duplicate handling**: Suggest using PATCH for updates instead of creating duplicates

### Step 5: Register the Router

Add your new router to the FastAPI application.

**Update** `backend/app/main.py`:

```python
from fastapi import FastAPI
from app.api.v1 import models, benchmarks, benchmark_results
from app.api.v1 import extraction  # Add this import
from app.db import init_db

app = FastAPI(
    title="AI Model Catalogue API",
    description="Track AI model performance and public opinions",
    version="0.1.0",
)

# Register routers
app.include_router(models.router)
app.include_router(benchmarks.router)
app.include_router(benchmark_results.router)
app.include_router(extraction.router)  # Add this line


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    await init_db()


@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "AI Model Catalogue API",
        "version": "0.1.0",
        "docs": "/docs",
    }
```

### Step 6: Manual Testing

Before writing tests, verify the endpoint works with manual testing.

**Start the development server:**

```bash
cd backend
uv run uvicorn app.main:app --reload
```

**Test with the interactive docs** at http://localhost:8000/docs:

1. Navigate to `POST /api/v1/extract`
2. Click "Try it out"
3. Enter this test text:

```json
{
  "text": "Claude 3.5 Sonnet was released by Anthropic in June 2024. It's a powerful language model that excels at coding and analysis tasks. The model is available via API with a commercial license."
}
```

4. Click "Execute"

**Expected response (201 Created):**

```json
{
  "model": {
    "id": 1,
    "name": "claude-3.5-sonnet",
    "organization": "Anthropic",
    "release_date": "2024-06-01",
    "description": "A powerful language model that excels at coding and analysis tasks",
    "license": "Proprietary",
    "created_at": "2025-12-31T10:30:00",
    "updated_at": "2025-12-31T10:30:00"
  },
  "tokens_used": 645,
  "llm_model": "claude-sonnet-4-5"
}
```

**Test duplicate detection:**

Run the same request again. You should get:

```json
{
  "detail": "Model 'claude-3.5-sonnet' already exists with ID 1. Use PATCH /api/v1/models/1 to update it."
}
```

Status code: `409 Conflict`

**Test with invalid text:**

```json
{
  "text": "This is just random text about nothing in particular."
}
```

Expected response:

```json
{
  "detail": "No model information could be extracted from the provided text. Please ensure the text contains information about an AI model."
}
```

Status code: `400 Bad Request`

**Test with empty text:**

```json
{
  "text": ""
}
```

Expected: `422 Unprocessable Entity` (Pydantic validation fails due to `min_length=10`)

### Step 7: Write Comprehensive Tests

Now create thorough tests for the extraction endpoint.

**Create** `backend/tests/test_extraction_api.py`:

```python
"""
Tests for Extraction API Endpoint

Tests the complete extraction pipeline: LLM → validation → database insertion
"""

import pytest
from datetime import date
from unittest.mock import AsyncMock, Mock, patch
from httpx import AsyncClient, ASGITransport
from sqlmodel.ext.asyncio.session import AsyncSession

from app.main import app
from app.services.llm_service import ExtractionResult, ExtractedModel
from app.models import Model
from app.db.repositories import ModelRepository


@pytest.fixture
def mock_extraction_result():
    """Mock successful LLM extraction result"""
    extracted = ExtractedModel(
        model_name="gpt-4",
        organization="OpenAI",
        release_date=date(2023, 3, 14),
        description="A large multimodal model",
        license="Proprietary",
    )

    return ExtractionResult(
        data=extracted,
        tokens_used=650,
        model_used="claude-sonnet-4-5",
    )


@pytest.mark.asyncio
class TestExtractEndpoint:
    """Test POST /api/v1/extract endpoint"""

    async def test_successful_extraction_and_creation(
        self, db_session: AsyncSession, mock_extraction_result
    ):
        """Extract model data and create in database"""

        # Mock LLMService.extract_model_data
        with patch("app.api.v1.extraction.LLMService") as MockLLMService:
            mock_service = MockLLMService.return_value
            mock_service.extract_model_data = AsyncMock(
                return_value=mock_extraction_result
            )

            # Make request
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.post(
                    "/api/v1/extract",
                    json={
                        "text": "GPT-4 was released by OpenAI in March 2023..."
                    },
                )

        # Verify response
        assert response.status_code == 201
        data = response.json()

        assert data["model"]["name"] == "gpt-4"
        assert data["model"]["organization"] == "OpenAI"
        assert data["model"]["release_date"] == "2023-03-14"
        assert data["model"]["description"] == "A large multimodal model"
        assert data["tokens_used"] == 650
        assert data["llm_model"] == "claude-sonnet-4-5"

        # Verify model was created in database
        repo = ModelRepository(db_session)
        created = await repo.get_by_name("gpt-4")
        assert created is not None
        assert created.organization == "OpenAI"


    async def test_duplicate_model_returns_409(
        self, db_session: AsyncSession, mock_extraction_result
    ):
        """Attempting to create duplicate model returns 409 Conflict"""

        # Create existing model
        repo = ModelRepository(db_session)
        existing = Model(
            name="gpt-4",
            organization="OpenAI",
            description="Existing model",
        )
        await repo.create(existing)

        # Mock LLM to extract same model
        with patch("app.api.v1.extraction.LLMService") as MockLLMService:
            mock_service = MockLLMService.return_value
            mock_service.extract_model_data = AsyncMock(
                return_value=mock_extraction_result
            )

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.post(
                    "/api/v1/extract",
                    json={"text": "GPT-4 by OpenAI..."},
                )

        # Verify 409 Conflict
        assert response.status_code == 409
        data = response.json()
        assert "already exists" in data["detail"]
        assert "PATCH" in data["detail"]  # Suggests update endpoint


    async def test_no_data_extracted_returns_400(self, db_session: AsyncSession):
        """LLM finds no model information returns 400"""

        # Mock LLM returning None (no data found)
        empty_result = ExtractionResult(
            data=None,  # No model found
            tokens_used=200,
            model_used="claude-sonnet-4-5",
        )

        with patch("app.api.v1.extraction.LLMService") as MockLLMService:
            mock_service = MockLLMService.return_value
            mock_service.extract_model_data = AsyncMock(return_value=empty_result)

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.post(
                    "/api/v1/extract",
                    json={"text": "This text has no model information"},
                )

        assert response.status_code == 400
        data = response.json()
        assert "No model information could be extracted" in data["detail"]


    async def test_empty_text_returns_422(self):
        """Empty text fails Pydantic validation"""

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/extract",
                json={"text": ""},  # Too short (min_length=10)
            )

        assert response.status_code == 422
        data = response.json()
        assert "validation error" in data["detail"][0]["type"]


    async def test_llm_error_returns_500(self, db_session: AsyncSession):
        """LLM API failure returns 500"""

        with patch("app.api.v1.extraction.LLMService") as MockLLMService:
            mock_service = MockLLMService.return_value
            mock_service.extract_model_data = AsyncMock(
                side_effect=Exception("Claude API timeout")
            )

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.post(
                    "/api/v1/extract",
                    json={"text": "GPT-4 by OpenAI..."},
                )

        assert response.status_code == 500
        data = response.json()
        assert "Failed to extract data" in data["detail"]


class TestExtractionHelpers:
    """Test helper functions"""

    def test_convert_extracted_to_create(self):
        """Field mapping works correctly"""
        from app.api.v1.extraction_helpers import convert_extracted_to_create

        extracted = ExtractedModel(
            model_name="llama-2",  # Note: model_name
            organization="Meta",
            release_date=date(2023, 7, 18),
            description="Open source LLM",
            license="Apache 2.0",
        )

        model_create = convert_extracted_to_create(extracted)

        assert model_create.name == "llama-2"  # Mapped to 'name'
        assert model_create.organization == "Meta"
        assert model_create.release_date == date(2023, 7, 18)
        assert model_create.description == "Open source LLM"
        assert model_create.license == "Apache 2.0"


    def test_validate_extracted_data_with_none(self):
        """Validation raises 400 for None data"""
        from app.api.v1.extraction_helpers import validate_extracted_data
        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            validate_extracted_data(None)

        assert exc_info.value.status_code == 400
        assert "No model information" in exc_info.value.detail


    def test_validate_extracted_data_with_valid(self):
        """Validation passes for valid data"""
        from app.api.v1.extraction_helpers import validate_extracted_data

        extracted = ExtractedModel(
            model_name="gpt-4",
            organization="OpenAI",
            release_date=None,  # Optional field
            description="Test model",
            license=None,  # Optional field
        )

        # Should not raise
        validate_extracted_data(extracted)


@pytest.mark.slow
@pytest.mark.asyncio
class TestRealExtractionIntegration:
    """Integration test with real Claude API (marked as slow)"""

    async def test_extract_real_gpt4_text(self, db_session: AsyncSession):
        """End-to-end test with real LLM API"""
        from app.config import settings

        if not settings.anthropic_api_key:
            pytest.skip("ANTHROPIC_API_KEY not configured")

        text = """
        GPT-4 is a large multimodal model developed by OpenAI.
        It was released on March 14, 2023, and represents a significant
        advancement in AI capabilities. The model accepts both text and
        image inputs and produces text outputs. GPT-4 is available under
        a proprietary license via OpenAI's API.
        """

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/extract",
                json={"text": text},
            )

        assert response.status_code == 201
        data = response.json()

        # Verify extraction accuracy
        assert data["model"]["name"] == "gpt-4"
        assert data["model"]["organization"] == "OpenAI"
        assert data["model"]["release_date"] == "2023-03-14"
        assert "multimodal" in data["model"]["description"].lower()
        assert data["model"]["license"] == "Proprietary"
        assert data["tokens_used"] > 0

        # Clean up - delete created model
        repo = ModelRepository(db_session)
        await repo.delete(data["model"]["id"])
```

**Run the tests:**

```bash
# Fast tests (mocked LLM)
uv run pytest tests/test_extraction_api.py::TestExtractEndpoint -v

# Helper function tests
uv run pytest tests/test_extraction_api.py::TestExtractionHelpers -v

# Slow test with real API (costs ~$0.01)
uv run pytest tests/test_extraction_api.py::TestRealExtractionIntegration -v --run-slow
```

### Step 8: Add pytest Marks Configuration

The tests use `@pytest.mark.slow` for real API tests. Configure pytest to handle this.

**Update** `backend/pytest.ini`:

```ini
[pytest]
markers =
    unit: Unit tests (fast, no external dependencies)
    slow: Slow tests that hit real external APIs
    integration: Integration tests with database

# Don't run slow tests by default
addopts = -m "not slow"
```

**Running different test suites:**

```bash
# All fast tests (default)
uv run pytest

# Include slow tests
uv run pytest -m ""

# Only slow tests
uv run pytest -m slow

# Only unit tests
uv run pytest -m unit
```

---

## Complete Example: Extraction Endpoint in Action

Let's trace a complete request through the system to solidify understanding.

**User request:**

```bash
POST /api/v1/extract HTTP/1.1
Content-Type: application/json

{
  "text": "Gemini 1.5 Pro was announced by Google in February 2024. It features a 1 million token context window and excels at long-document understanding. The model is available via Google's Vertex AI platform under a commercial license."
}
```

**Processing flow:**

```python
# 1. FastAPI receives request, validates ExtractRequest schema
request = ExtractRequest(text="Gemini 1.5 Pro was announced...")

# 2. Dependency injection provides LLMService instance
llm_service = get_llm_service()  # Singleton instance

# 3. Extract data using Claude
extraction_result = await llm_service.extract_model_data(
    text=request.text,
    use_cache=True
)
# Returns: ExtractionResult(
#     data=ExtractedModel(
#         model_name="gemini-1.5-pro",
#         organization="Google",
#         release_date=date(2024, 2, 1),
#         description="Features 1M token context, excels at long docs",
#         license="Proprietary"
#     ),
#     tokens_used=720,
#     model_used="claude-sonnet-4-5"
# )

# 4. Validate extraction produced data
validate_extracted_data(extraction_result.data)  # Passes

# 5. Convert to ModelCreate
model_create = convert_extracted_to_create(extraction_result.data)
# Returns: ModelCreate(
#     name="gemini-1.5-pro",  # Field name mapped!
#     organization="Google",
#     ...
# )

# 6. Check for duplicates
repo = ModelRepository(session)
existing = await repo.get_by_name("gemini-1.5-pro")  # None (new model)

# 7. Create in database
new_model = Model(**model_create.model_dump())
created = await repo.create(new_model)
# Returns: Model(id=5, name="gemini-1.5-pro", created_at=..., ...)

# 8. Build response
response = ExtractResponse(
    model=created,  # Automatically converts to ModelResponse
    tokens_used=720,
    llm_model="claude-sonnet-4-5"
)
```

**Response (201 Created):**

```json
{
  "model": {
    "id": 5,
    "name": "gemini-1.5-pro",
    "organization": "Google",
    "release_date": "2024-02-01",
    "description": "Features 1M token context, excels at long docs",
    "license": "Proprietary",
    "created_at": "2025-12-31T14:22:00.000Z",
    "updated_at": "2025-12-31T14:22:00.000Z"
  },
  "tokens_used": 720,
  "llm_model": "claude-sonnet-4-5"
}
```

**Token cost calculation:**

```python
# Claude Sonnet pricing (December 2025)
INPUT_COST = $3.00 / 1M tokens
OUTPUT_COST = $15.00 / 1M tokens

# Breakdown (assuming 600 input, 120 output tokens)
input_cost = (600 / 1_000_000) * 3.00 = $0.0018
output_cost = (120 / 1_000_000) * 15.00 = $0.0018
total_cost = $0.0036  # Less than half a cent per extraction!

# With prompt caching (90% cache hit):
cache_cost = (60 / 1_000_000) * 0.30 = $0.000018  # Cache reads are 10x cheaper
total_with_cache = $0.0004  # ~10x cheaper with caching
```

---

## Testing Your Implementation

### Manual Testing Checklist

Test each scenario manually using the interactive docs at `/docs`:

- [ ] **Happy path**: Extract a well-formed model description
- [ ] **Duplicate detection**: Try extracting the same model twice
- [ ] **No data found**: Submit text with no model information
- [ ] **Empty text**: Submit an empty string (should get 422)
- [ ] **Partial data**: Text with only model name and organization
- [ ] **Token usage**: Verify `tokens_used` appears in response
- [ ] **Database persistence**: Check model exists with `GET /api/v1/models`

### Automated Test Suite

Run the complete test suite:

```bash
# Unit tests (fast, mocked)
uv run pytest tests/test_extraction_api.py::TestExtractEndpoint -v

# Helper function tests
uv run pytest tests/test_extraction_api.py::TestExtractionHelpers -v

# Integration test with real API (slow, costs ~$0.01)
uv run pytest tests/test_extraction_api.py::TestRealExtractionIntegration -v -m slow
```

**Expected output:**

```
tests/test_extraction_api.py::TestExtractEndpoint::test_successful_extraction_and_creation PASSED
tests/test_extraction_api.py::TestExtractEndpoint::test_duplicate_model_returns_409 PASSED
tests/test_extraction_api.py::TestExtractEndpoint::test_no_data_extracted_returns_400 PASSED
tests/test_extraction_api.py::TestExtractEndpoint::test_empty_text_returns_422 PASSED
tests/test_extraction_api.py::TestExtractEndpoint::test_llm_error_returns_500 PASSED
tests/test_extraction_api.py::TestExtractionHelpers::test_convert_extracted_to_create PASSED
tests/test_extraction_api.py::TestExtractionHelpers::test_validate_extracted_data_with_none PASSED
tests/test_extraction_api.py::TestExtractionHelpers::test_validate_extracted_data_with_valid PASSED

========== 8 passed in 2.45s ==========
```

### Performance Testing

Test how the endpoint performs under load:

```bash
# Install Apache Bench
brew install httpd  # macOS
sudo apt-get install apache2-utils  # Linux

# Create test payload
cat > extract_request.json << EOF
{
  "text": "Claude 3 Opus was released by Anthropic in March 2024. It's their most capable model for complex reasoning tasks."
}
EOF

# Run 10 requests
ab -n 10 -c 1 -p extract_request.json -T application/json \
  http://localhost:8000/api/v1/extract
```

**Expected results:**

- **Mean response time**: 1-2 seconds (depends on Claude API latency)
- **Token usage consistency**: Similar token counts across requests (caching working)
- **Error rate**: 0% (all successful or duplicate errors)

---

## Hands-On Exercises

### Exercise 1: Enhanced Error Messages

**Objective:** Improve error messages with extraction hints.

**Current behavior:**
```json
{"detail": "No model information could be extracted from the provided text."}
```

**Enhanced behavior:**
```json
{
  "detail": "No model information could be extracted from the provided text.",
  "extracted_entities": ["Google", "2024"],
  "suggestions": [
    "Ensure the text mentions a model name (e.g., GPT-4, Claude, Llama)",
    "Include organization name and release date if available"
  ]
}
```

**Instructions:**

1. Modify `ExtractErrorResponse` to include `extracted_entities` and `suggestions` fields
2. Update `validate_extracted_data()` to populate these fields
3. Add logic to detect partial extractions (organization but no model name)
4. Test with various incomplete text samples

**Acceptance Criteria:**

- Error responses include helpful extraction hints
- Partial extractions are identified and reported
- Tests verify new response format

**Hint:** You can pass metadata through the validation function:

```python
def validate_extracted_data(extracted: ExtractedModel | None, original_text: str):
    if extracted is None:
        # Analyze original_text to provide hints
        entities = extract_entities(original_text)  # Helper function
        raise HTTPException(
            status_code=400,
            detail={
                "message": "No model information found",
                "extracted_entities": entities,
                "suggestions": generate_suggestions(entities)
            }
        )
```

### Exercise 2: Batch Extraction Endpoint

**Objective:** Create an endpoint that extracts multiple models from a single text.

**Use case:** Research papers often mention multiple models:

```text
"In our comparison, GPT-4 scored 86%, Claude 3 Opus scored 84%,
and Gemini 1.5 Pro scored 82% on the MMLU benchmark."
```

**Requirements:**

1. Create `POST /api/v1/extract/batch` endpoint
2. Accept `BatchExtractRequest` with `text` field
3. Extract all models mentioned in the text
4. Return list of created models with total token usage
5. Handle partial failures (some models already exist)

**Schema design:**

```python
class BatchExtractResponse(BaseModel):
    models: list[ModelResponse]
    duplicates: list[str]  # Names of models that already existed
    tokens_used: int
    llm_model: str
```

**Acceptance Criteria:**

- Endpoint creates multiple models from single text
- Duplicate models are reported but don't cause failure
- Response indicates which models were created vs skipped
- Tests verify multi-model extraction

**Hint:** Modify the LLM prompt to return a list:

```python
# In LLMService, create new method:
async def extract_multiple_models(self, text: str) -> list[ExtractedModel]:
    """Extract all models mentioned in text"""
    # Prompt: "Extract ALL models mentioned, return as JSON array"
```

### Exercise 3: Extraction Confidence Scoring

**Objective:** Add confidence scores to indicate extraction reliability.

**Implementation:**

1. Modify `ExtractedModel` to include `confidence: float` field (0.0-1.0)
2. Update Claude prompt to include confidence assessment
3. In endpoint, warn users about low-confidence extractions
4. Add `require_high_confidence` query parameter (default: False)

**Prompt addition:**

```python
SYSTEM_PROMPT = """
...
For each field, assess your confidence (0.0-1.0):
- 1.0: Explicitly stated in text
- 0.7: Strongly implied
- 0.5: Weak inference
- 0.0: Complete guess

Return confidence in metadata field.
"""
```

**Response format:**

```json
{
  "model": {...},
  "tokens_used": 650,
  "llm_model": "claude-sonnet-4-5",
  "confidence": 0.95,
  "low_confidence_fields": []
}
```

**Acceptance Criteria:**

- Confidence scores reflect extraction quality
- Low-confidence extractions can be rejected with query param
- Tests verify confidence thresholds

---

## Common Pitfalls

### Pitfall 1: Not Converting Field Names

**Symptom:**
```python
# Error: Model has no attribute 'model_name'
created = await repo.create(Model(**extracted.model_dump()))
```

**Problem:** `ExtractedModel` uses `model_name`, but `Model` uses `name`.

**Solution:** Always use the conversion helper:

```python
model_create = convert_extracted_to_create(extracted)  # Maps fields
created = await repo.create(Model(**model_create.model_dump()))
```

### Pitfall 2: Forgetting Duplicate Checks

**Symptom:** Database raises IntegrityError when creating duplicate models.

**Problem:** Not checking `get_by_name()` before creating.

**Solution:**

```python
existing = await repo.get_by_name(model_create.name)
if existing:
    raise HTTPException(409, f"Model '{model_create.name}' already exists")
```

### Pitfall 3: Poor Error Messages

**Symptom:** Users see generic "500 Internal Server Error" for LLM failures.

**Problem:** Not catching specific exceptions.

**Solution:**

```python
try:
    result = await llm_service.extract_model_data(text)
except ValueError as e:
    # Client errors (empty text, etc.)
    raise HTTPException(400, str(e))
except Exception as e:
    # Server errors (API failures, etc.)
    logger.error(f"LLM extraction failed: {e}")
    raise HTTPException(500, "Failed to extract data")
```

### Pitfall 4: Not Using Dependency Injection

**Symptom:** Tests fail because they can't mock `LLMService`.

**Problem:** Creating service directly in endpoint:

```python
# ❌ Hard to test
@router.post("/extract")
async def extract(text: str):
    llm_service = LLMService()  # Can't mock this!
```

**Solution:** Use dependency injection:

```python
# ✅ Testable
@router.post("/extract")
async def extract(
    text: str,
    llm_service: LLMService = Depends(get_llm_service)  # Mockable!
):
```

### Pitfall 5: Ignoring Token Usage

**Symptom:** Unexpected API bills.

**Problem:** Not monitoring token consumption.

**Solution:**

```python
# Log token usage for monitoring
logger.info(f"Extraction used {result.tokens_used} tokens")

# Return in response for user awareness
return ExtractResponse(
    model=created,
    tokens_used=result.tokens_used,  # Make users aware of costs
    llm_model=result.model_used
)
```

### Pitfall 6: Validating After Database Insertion

**Symptom:** Invalid data gets into database before validation catches it.

**Problem:** Wrong order of operations:

```python
# ❌ Wrong order
created = await repo.create(model)  # Insert first
validate_extracted_data(extracted)  # Validate after (too late!)
```

**Solution:** Validate before any database operations:

```python
# ✅ Correct order
validate_extracted_data(extraction_result.data)  # Validate first
existing = await repo.get_by_name(model_create.name)  # Then check duplicates
created = await repo.create(model)  # Finally insert
```

---

## Key Takeaways

**Architecture Patterns:**

- **Service orchestration**: Endpoints coordinate multiple services (LLM + Repository)
- **Dependency injection**: Use `Depends()` for testable, reusable services
- **Schema mapping**: Convert between LLM schemas and database schemas explicitly
- **Defense in depth**: Validate at multiple layers (Pydantic, business logic, database)

**Error Handling:**

- **Appropriate status codes**: 400 (client error), 409 (conflict), 500 (server error)
- **Clear error messages**: Tell users exactly what went wrong and how to fix it
- **Graceful degradation**: Partial failures shouldn't crash the system
- **Comprehensive logging**: Log each step for debugging and monitoring

**LLM Integration:**

- **Never trust AI outputs**: Always validate before database insertion
- **Monitor token usage**: Return in responses for cost awareness
- **Handle extraction failures**: LLMs can't always extract data - that's okay
- **Use prompt caching**: Reduce costs with `use_cache=True`

**Testing:**

- **Mock external services**: Don't hit real APIs in unit tests
- **Test error paths**: Duplicates, missing data, API failures
- **Use pytest marks**: Separate slow (real API) from fast (mocked) tests
- **Integration tests**: Verify end-to-end pipeline occasionally

**What Makes This Production-Ready:**

1. ✅ Comprehensive error handling with clear messages
2. ✅ Duplicate detection before database insertion
3. ✅ Proper HTTP status codes for different error types
4. ✅ Logging for debugging and monitoring
5. ✅ Testable architecture with dependency injection
6. ✅ Cost awareness through token usage reporting
7. ✅ Helpful documentation in OpenAPI schema
8. ✅ Multi-layer validation (Pydantic + business + database)

---

## Further Reading

**FastAPI Patterns:**

- **Dependency Injection**: https://fastapi.tiangolo.com/tutorial/dependencies/
- **Error Handling**: https://fastapi.tiangolo.com/tutorial/handling-errors/
- **Response Models**: https://fastapi.tiangolo.com/tutorial/response-model/

**LLM Integration Best Practices:**

- **Structured Outputs**: https://docs.anthropic.com/en/docs/build-with-claude/structured-outputs
- **Prompt Engineering**: https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering
- **Error Handling**: https://docs.anthropic.com/en/api/errors

**Testing Strategies:**

- **pytest Fixtures**: https://docs.pytest.org/en/stable/fixture.html
- **Async Testing**: https://pytest-asyncio.readthedocs.io/
- **Mocking**: https://docs.python.org/3/library/unittest.mock.html

**Architecture:**

- **Service Layer Pattern**: https://martinfowler.com/eaaCatalog/serviceLayer.html
- **Repository Pattern**: https://martinfowler.com/eaaCatalog/repository.html

---

## Next Steps

Congratulations! You've built a complete manual extraction pipeline. Users can now paste text about AI models and automatically populate your catalogue using Claude.

**What you've accomplished:**

- ✅ Created a production-ready extraction endpoint
- ✅ Integrated LLM service with repository layer
- ✅ Implemented comprehensive error handling
- ✅ Built testable architecture with dependency injection
- ✅ Validated LLM outputs before database insertion
- ✅ Monitored token usage for cost awareness

**In Module 4.1 (RSS Feed Parser & Scheduler)**, you'll:

1. Set up APScheduler for weekday cron jobs
2. Parse RSS feeds with feedparser
3. Extract newsletter content automatically
4. Schedule daily model updates
5. Implement error recovery and monitoring

**Preview of Module 4.1:**

```python
# Scheduled job that runs Monday-Friday at 9 AM
@scheduler.scheduled_job("cron", hour=9, day_of_week="mon-fri")
async def ingest_daily_newsletter():
    """
    Fetch RSS feed, extract model updates, insert into database.
    """
    # Fetch RSS feed
    feed = feedparser.parse(settings.rss_feed_url)

    for entry in feed.entries:
        # Extract text from entry
        text = f"{entry.title}\n\n{entry.summary}"

        # Use your extraction endpoint logic
        result = await llm_service.extract_model_data(text)

        # Insert if new model found
        if result.data:
            await create_or_update_model(result.data)
```

This will complete your automated data ingestion pipeline, making your Model Catalogue truly hands-off!

**Optional Challenge:** Before starting Module 4.1, try implementing a simple scheduler yourself. Can you create a script that runs your extraction endpoint on a timer? This will prepare you for the full RSS integration.
