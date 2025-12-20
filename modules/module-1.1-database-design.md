# Module 1.1: Database Design & Setup - The Foundation of Data

**Duration:** 2 hours
**Difficulty:** Intermediate
**Prerequisites:** Module 0 complete, basic SQL knowledge helpful (but not required)

---

## Introduction: Why Database Design Matters

You've built the application skeleton. Now it's time to design the heart of your system: the database.

A well-designed database is like a well-organized library. Every piece of information has its proper place, relationships are clear, and finding what you need is fast and efficient. A poorly designed database? That's like throwing books randomly on shelves—eventually, you'll find what you need, but it'll be slow, painful, and error-prone.

In this module, you'll learn the art and science of **relational database design**. You'll understand:

- **Why normalization matters** (and when to break the rules)
- **How to model relationships** between entities
- **When to use advanced features** like JSONB and array columns
- **How to set up indexes** for performance from day one
- **How database migrations** let you evolve your schema safely

But here's what makes this module special: you'll learn to use **SQLModel**, a modern library that combines the power of SQLAlchemy's ORM with Pydantic's validation in a single unified model. No more maintaining duplicate definitions—one model class will serve as both your database table and your API schema.

Most importantly, you'll learn to think in terms of **data integrity**—ensuring your database can't get into an invalid state, even when things go wrong.

This isn't just theory. You'll create a real database on Supabase (managed PostgreSQL), design a production-ready schema for the AI Model Catalogue, and write your first database migration.

---

## What You'll Build

By the end of this module, you'll have:

- ✅ A Supabase project with PostgreSQL database
- ✅ Understanding of database normalization and when to use it
- ✅ Complete schema design for 5 core entities (Models, Benchmarks, Results, Opinions, UseCases)
- ✅ SQLModel models that serve double duty as tables AND schemas
- ✅ Alembic configured for database migrations
- ✅ Initial migration creating all tables with proper constraints
- ✅ Schema deployed to Supabase and verified
- ✅ Async database connection tests to validate setup

---

## Understanding SQLModel: The Best of Both Worlds

Before we dive into database design, let's understand why we're using SQLModel instead of plain SQLAlchemy.

### The Traditional Problem

In typical FastAPI + SQLAlchemy projects, you maintain duplicate definitions:

```python
# SQLAlchemy model for the database
class ModelDB(Base):
    __tablename__ = "models"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    organization = Column(String, nullable=False)

# Pydantic schema for API validation
class ModelCreate(BaseModel):
    name: str
    organization: str

# Pydantic schema for API responses
class ModelResponse(BaseModel):
    id: int
    name: str
    organization: str

    class Config:
        from_attributes = True
```

**The problem:** You're defining the same fields three times! Any change means updating multiple classes. It's tedious and error-prone.

### The SQLModel Solution

SQLModel, created by the same author as FastAPI, unifies these definitions:

```python
from sqlmodel import SQLModel, Field

# Base model with shared fields
class ModelBase(SQLModel):
    name: str
    organization: str

# Table model for database
class Model(ModelBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

# Schema models for API (inherit from base)
class ModelCreate(ModelBase):
    pass

class ModelResponse(ModelBase):
    id: int
```

**The benefits:**

1. **Single source of truth**: Define fields once in the base model
2. **Type safety**: Full editor support with type hints
3. **Pydantic validation**: Automatic validation on all models
4. **SQLAlchemy underneath**: All SQLAlchemy features still available
5. **FastAPI integration**: Works seamlessly with FastAPI
6. **Reduced code**: Less boilerplate, more clarity

### How SQLModel Works

SQLModel is built on top of SQLAlchemy and Pydantic:

```
┌─────────────────────────────────────────────┐
│              Your SQLModel Classes          │
│   (ModelBase, Model, ModelCreate, etc.)     │
└─────────────────┬───────────────────────────┘
                  │
         ┌────────┴────────┐
         ▼                 ▼
  ┌─────────────┐   ┌─────────────┐
  │ SQLAlchemy  │   │  Pydantic   │
  │   (ORM)     │   │(Validation) │
  └─────────────┘   └─────────────┘
         │                 │
         ▼                 ▼
    Database           API I/O
```

**Key insight:** SQLModel models ARE SQLAlchemy models AND Pydantic models simultaneously. You get the best of both worlds.

---

## Step 1: Understanding Relational Database Design

Before we write any code, let's understand the principles that will guide our decisions.

### The Problem: Data Redundancy and Inconsistency

Imagine storing AI model data like this:

```
| model_name | organization | benchmark_name | score | benchmark_category |
|------------|--------------|----------------|-------|-------------------|
| GPT-4      | OpenAI       | MMLU           | 86.4  | Knowledge         |
| GPT-4      | OpenAI       | HumanEval      | 67.0  | Coding            |
| Claude 3   | Anthropic    | MMLU           | 86.8  | Knowledge         |
```

**What's wrong here?**

- Model info (GPT-4, OpenAI) is repeated for every benchmark result—wasted space
- If OpenAI changes their name, we'd need to update hundreds of rows
- If we accidentally type "0penAI" (with a zero), we've created data inconsistency
- No way to add a model without benchmark results

### The Solution: Normalization

**Normalization** is the process of organizing data to reduce redundancy. We split data into separate tables and link them with **foreign keys**:

```
Models:
| id | name     | organization |
|----|----------|--------------|
| 1  | GPT-4    | OpenAI       |
| 2  | Claude 3 | Anthropic    |

Benchmarks:
| id | name      | category  |
|----|-----------|-----------|
| 1  | MMLU      | Knowledge |
| 2  | HumanEval | Coding    |

BenchmarkResults:
| id | model_id | benchmark_id | score |
|----|----------|--------------|-------|
| 1  | 1        | 1            | 86.4  |
| 2  | 1        | 2            | 67.0  |
| 3  | 2        | 1            | 86.8  |
```

**Benefits:**

- Each fact stored once (Single Source of Truth)
- Updates happen in one place
- No inconsistencies possible
- Can add models/benchmarks independently

### When to Break the Rules: Denormalization

Sometimes, we intentionally add redundancy for **performance** or **flexibility**:

**JSONB columns** for flexible metadata:

```python
# Instead of creating separate tables for every possible model attribute,
# use JSONB for data that varies by model:
metadata = {
    "context_window": 128000,
    "multimodal": True,
    "pricing": {"input": 0.03, "output": 0.06}
}
```

**Array columns** for simple lists:

```python
# For opinions, tags are simple strings without relationships:
tags = ["coding", "creative-writing", "analysis"]
```

**The Rule:** Normalize by default. Denormalize deliberately when you have a good reason (performance, flexibility, simplicity).

**🎯 Checkpoint:** Understand the trade-off: normalization prevents inconsistency, but sometimes flexibility or performance matters more.

---

## Step 2: Designing the Schema - The Entity Relationship Model

Let's design the five core entities for our AI Model Catalogue.

### Entity 1: Models

**Purpose:** Store information about AI models (GPT-4, Claude, Llama, etc.)

```python
Models:
- id: Integer (Primary Key, auto-increment)
- name: String (unique, required) - e.g., "GPT-4", "Claude 3 Opus"
- organization: String (required) - e.g., "OpenAI", "Anthropic"
- release_date: Date (nullable) - when the model was released
- description: Text (nullable) - summary of capabilities
- license: String (nullable) - e.g., "Apache 2.0", "Proprietary"
- metadata: JSONB (nullable) - flexible data (pricing, context_window, etc.)
- created_at: Timestamp (auto-set)
- updated_at: Timestamp (auto-update)
```

**Why JSONB for metadata?** Different models have different attributes. GPT-4 has vision capabilities, Claude has thinking modes. Rather than creating 50 columns (most empty), we use JSONB for flexibility.

### Entity 2: Benchmarks

**Purpose:** Store academic benchmarks used to evaluate models

```python
Benchmarks:
- id: Integer (Primary Key)
- name: String (unique, required) - e.g., "MMLU", "HumanEval"
- category: String (nullable) - e.g., "Knowledge", "Coding", "Math"
- description: Text (nullable) - what the benchmark measures
- url: String (nullable) - link to benchmark paper/website
- created_at: Timestamp
- updated_at: Timestamp
```

### Entity 3: BenchmarkResults

**Purpose:** The "join table" linking models to benchmarks with scores

```python
BenchmarkResults:
- id: Integer (Primary Key)
- model_id: Integer (Foreign Key → Models.id, required)
- benchmark_id: Integer (Foreign Key → Benchmarks.id, required)
- score: Float (required) - the actual performance score
- date_tested: Date (nullable) - when the test was run
- source: String (nullable) - who reported the result (e.g., "OpenAI", "LMSYS")
- created_at: Timestamp
- updated_at: Timestamp

Constraints:
- UNIQUE (model_id, benchmark_id, date_tested) - prevent duplicate results
```

**Why the unique constraint?** We don't want the same model+benchmark+date recorded twice. But we DO allow multiple results over time (date_tested varies).

### Entity 4: Opinions

**Purpose:** Store public opinions about models from various sources

```python
Opinions:
- id: Integer (Primary Key)
- model_id: Integer (Foreign Key → Models.id, required)
- content: Text (required) - the opinion text
- sentiment: String (nullable) - "positive", "negative", "neutral", "mixed"
- source: String (nullable) - where it came from (e.g., "Twitter", "Reddit")
- author: String (nullable) - who said it
- date_published: Date (nullable)
- tags: Array of Strings (nullable) - ["coding", "creative-writing"]
- created_at: Timestamp
- updated_at: Timestamp
```

**Why an array for tags?** Tags are simple labels without relationships. They don't need their own table—an array is perfect.

### Entity 5: UseCases

**Purpose:** Track mentioned use cases for each model

```python
UseCases:
- id: Integer (Primary Key)
- model_id: Integer (Foreign Key → Models.id, required)
- use_case: String (required) - e.g., "code generation", "customer support"
- description: Text (nullable) - more detail about the use case
- mentioned_by: String (nullable) - source of the mention
- created_at: Timestamp
- updated_at: Timestamp
```

### Relationships Summary

```
Models (1) ←→ (Many) BenchmarkResults ←→ (1) Benchmarks
  ↓
  ├→ (Many) Opinions
  └→ (Many) UseCases
```

**In plain English:**

- One model can have many benchmark results
- One benchmark can have results from many models
- One model can have many opinions
- One model can have many use cases

**🎯 Checkpoint:** Draw this relationship diagram on paper. Understanding relationships visually helps when writing queries later.

---

## Step 3: Creating a Supabase Project

Supabase provides managed PostgreSQL with a fantastic UI, automatic backups, and built-in APIs. Let's set it up.

### Sign Up for Supabase

1. Go to [https://supabase.com](https://supabase.com)
2. Click "Start your project"
3. Sign in with GitHub (recommended for developers)

### Create a New Project

1. Click "New Project"
2. Choose your organization (or create one)
3. Fill in project details:

   - **Name:** `model-catalogue` (or whatever you prefer)
   - **Database Password:** Generate a strong password (save it in a password manager!)
   - **Region:** Choose the closest to you (for lowest latency)
   - **Pricing Plan:** Free tier is perfect for learning

4. Click "Create new project" and wait ~2 minutes for provisioning

### Get Your Database Credentials

Once your project is ready:

1. Click on the **Connect** button in the top right
2. Select "Direct Connection" mode
3. Copy the **URI** (it should look like):

```
postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
```

4. Replace `[YOUR-PASSWORD]` with the database password you set earlier

**Note:** Supabase provides two connection modes:

- **Session mode** (port 5432) - Direct connection, for migrations
- **Transaction mode** (port 6543) - Pooled connections, for application

For now, use the **Session mode** connection string (change port to 5432):

```
postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
```

### Update Your .env File

Open your `.env` file and update the `DATABASE_URL`:

```bash
# .env
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
```

**Security Note:** The `.env` file is in `.gitignore` and will NEVER be committed to version control. Anyone with this URL can access your database—treat it like a password!

**🎯 Checkpoint:** Your `DATABASE_URL` environment variable is set. We'll test the connection in a later step.

---

## Step 4: Creating SQLModel Models - The Unified Approach

Now comes the exciting part: defining our database schema using SQLModel's unified model approach.

### Understanding SQLModel's Model Patterns

SQLModel uses three types of models:

1. **Base Models** (`table=False`, default): Shared fields, not database tables
2. **Table Models** (`table=True`): Actual database tables
3. **Schema Models** (inherit from base): For API validation and responses

**The pattern:**

```python
# Step 1: Define base model with shared fields
class ModelBase(SQLModel):
    name: str
    organization: str

# Step 2: Define table model (inherits from base, adds id)
class Model(ModelBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

# Step 3: Define schema models for API
class ModelCreate(ModelBase):
    pass  # Inherits name, organization

class ModelResponse(ModelBase):
    id: int  # Required for responses
```

Let's implement this pattern for all our entities.

### Create the Base Configuration

Create `backend/app/models/base.py`:

```python
"""
SQLModel Base Configuration and Mixins
All models inherit from SQLModel or use mixins for common functionality
"""
from sqlmodel import SQLModel, Field
from datetime import datetime
from sqlalchemy import DateTime, func


class TimestampMixin(SQLModel):
    """
    Mixin that adds created_at and updated_at timestamps to models

    Usage:
        class MyModel(TimestampMixin, table=True):
            id: int | None = Field(default=None, primary_key=True)
            name: str
    """
    created_at: datetime | None = Field(
        default=None,
        sa_column_kwargs={
            "server_default": func.now(),
        },
        sa_type=DateTime(timezone=True),
    )
    updated_at: datetime | None = Field(
        default=None,
        sa_column_kwargs={
            "onupdate": func.now(),
        },
        sa_type=DateTime(timezone=True),
    )
```

**Why a mixin?** We'll add `created_at` and `updated_at` to every table. Rather than copy-pasting, we use a mixin—a reusable component that we can "mix in" to any model.

**Key SQLModel concepts here:**

- `Field(...)`: SQLModel's way to configure columns
- `sa_column_kwargs={...}`: Pass extra arguments to the underlying SQLAlchemy Column
- `server_default=func.now()`: PostgreSQL sets the timestamp automatically
- `onupdate=func.now()`: PostgreSQL updates timestamp on row modification

### Create the Table Models

Create `backend/app/models/models.py`:

```python
"""
Database Models for AI Model Catalogue

These SQLModel models define both:
1. Database tables (table=True models)
2. Pydantic schemas for validation (base models)

Alembic will auto-generate migrations from these definitions.
"""
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, Index, UniqueConstraint, String, Text
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from typing import Optional
from datetime import date, datetime

from .base import TimestampMixin


# =============================================================================
# Models Entity
# =============================================================================

class ModelBase(SQLModel):
    """Base model with shared fields for AI models"""
    name: str = Field(max_length=255, index=True, unique=True)
    organization: str = Field(max_length=255)
    release_date: date | None = Field(default=None)
    description: str | None = Field(default=None, sa_column=Column(Text))
    license: str | None = Field(default=None, max_length=255)


class Model(ModelBase, TimestampMixin, table=True):
    """
    Represents an AI model (e.g., GPT-4, Claude, Llama)

    This is the table definition that will be created in the database.
    """
    __tablename__ = "models"

    id: int | None = Field(default=None, primary_key=True)

    # JSONB for flexible metadata (pricing, context_window, capabilities, etc.)
    # Using sa_column because SQLModel doesn't directly support JSONB
    metadata_: dict | None = Field(
        default=None,
        sa_column=Column("metadata", JSONB, nullable=True)
    )

    # Relationships (loaded with queries)
    benchmark_results: list["BenchmarkResult"] = Relationship(
        back_populates="model",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    opinions: list["Opinion"] = Relationship(
        back_populates="model",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    use_cases: list["UseCase"] = Relationship(
        back_populates="model",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )


class ModelCreate(ModelBase):
    """Schema for creating a new model via API"""
    metadata_: dict | None = None


class ModelUpdate(SQLModel):
    """Schema for updating a model via API (all fields optional)"""
    name: str | None = None
    organization: str | None = None
    release_date: date | None = None
    description: str | None = None
    license: str | None = None
    metadata_: dict | None = None


class ModelResponse(ModelBase):
    """Schema for model in API responses"""
    id: int
    metadata_: dict | None = None
    created_at: datetime
    updated_at: datetime


# =============================================================================
# Benchmarks Entity
# =============================================================================

class BenchmarkBase(SQLModel):
    """Base model with shared fields for benchmarks"""
    name: str = Field(max_length=255, index=True, unique=True)
    category: str | None = Field(default=None, max_length=100, index=True)
    description: str | None = Field(default=None, sa_column=Column(Text))
    url: str | None = Field(default=None, max_length=500)


class Benchmark(BenchmarkBase, TimestampMixin, table=True):
    """
    Represents an academic benchmark used to evaluate AI models
    """
    __tablename__ = "benchmarks"

    id: int | None = Field(default=None, primary_key=True)

    # Relationships
    results: list["BenchmarkResult"] = Relationship(
        back_populates="benchmark",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )


class BenchmarkCreate(BenchmarkBase):
    """Schema for creating a new benchmark via API"""
    pass


class BenchmarkUpdate(SQLModel):
    """Schema for updating a benchmark via API (all fields optional)"""
    name: str | None = None
    category: str | None = None
    description: str | None = None
    url: str | None = None


class BenchmarkResponse(BenchmarkBase):
    """Schema for benchmark in API responses"""
    id: int
    created_at: datetime
    updated_at: datetime


# =============================================================================
# BenchmarkResults Entity (Join Table)
# =============================================================================

class BenchmarkResultBase(SQLModel):
    """Base model with shared fields for benchmark results"""
    score: float
    date_tested: date | None = Field(default=None)
    source: str | None = Field(default=None, max_length=255)


class BenchmarkResult(BenchmarkResultBase, TimestampMixin, table=True):
    """
    Represents a model's performance on a specific benchmark
    This is the "join table" between Models and Benchmarks, with extra data
    """
    __tablename__ = "benchmark_results"

    id: int | None = Field(default=None, primary_key=True)

    # Foreign Keys
    model_id: int = Field(foreign_key="models.id", index=True)
    benchmark_id: int = Field(foreign_key="benchmarks.id", index=True)

    # Relationships
    model: "Model" = Relationship(back_populates="benchmark_results")
    benchmark: "Benchmark" = Relationship(back_populates="results")

    # Constraints
    __table_args__ = (
        # Prevent duplicate results for the same model+benchmark on the same date
        UniqueConstraint(
            "model_id", "benchmark_id", "date_tested",
            name="uix_model_benchmark_date"
        ),
        # Composite index for common queries
        Index("ix_benchmark_results_model_benchmark", "model_id", "benchmark_id"),
    )


class BenchmarkResultCreate(BenchmarkResultBase):
    """Schema for creating a new benchmark result via API"""
    model_id: int
    benchmark_id: int


class BenchmarkResultUpdate(SQLModel):
    """Schema for updating a benchmark result via API (all fields optional)"""
    score: float | None = None
    date_tested: date | None = None
    source: str | None = None


class BenchmarkResultResponse(BenchmarkResultBase):
    """Schema for benchmark result in API responses"""
    id: int
    model_id: int
    benchmark_id: int
    created_at: datetime
    updated_at: datetime


# =============================================================================
# Opinions Entity
# =============================================================================

class OpinionBase(SQLModel):
    """Base model with shared fields for opinions"""
    content: str = Field(sa_column=Column(Text, nullable=False))
    sentiment: str | None = Field(default=None, max_length=50)
    source: str | None = Field(default=None, max_length=255)
    author: str | None = Field(default=None, max_length=255)
    date_published: date | None = Field(default=None, index=True)


class Opinion(OpinionBase, TimestampMixin, table=True):
    """
    Represents public opinion about a model from various sources
    """
    __tablename__ = "opinions"

    id: int | None = Field(default=None, primary_key=True)

    # Foreign Key
    model_id: int = Field(foreign_key="models.id", index=True)

    # PostgreSQL array for tags (e.g., ["coding", "creative-writing"])
    tags: list[str] | None = Field(
        default=None,
        sa_column=Column(ARRAY(String), nullable=True)
    )

    # Relationship
    model: "Model" = Relationship(back_populates="opinions")


class OpinionCreate(OpinionBase):
    """Schema for creating a new opinion via API"""
    model_id: int
    tags: list[str] | None = None


class OpinionUpdate(SQLModel):
    """Schema for updating an opinion via API (all fields optional)"""
    content: str | None = None
    sentiment: str | None = None
    source: str | None = None
    author: str | None = None
    date_published: date | None = None
    tags: list[str] | None = None


class OpinionResponse(OpinionBase):
    """Schema for opinion in API responses"""
    id: int
    model_id: int
    tags: list[str] | None = None
    created_at: datetime
    updated_at: datetime


# =============================================================================
# UseCases Entity
# =============================================================================

class UseCaseBase(SQLModel):
    """Base model with shared fields for use cases"""
    use_case: str = Field(max_length=255)
    description: str | None = Field(default=None, sa_column=Column(Text))
    mentioned_by: str | None = Field(default=None, max_length=255)


class UseCase(UseCaseBase, TimestampMixin, table=True):
    """
    Represents a mentioned use case for a model
    """
    __tablename__ = "use_cases"

    id: int | None = Field(default=None, primary_key=True)

    # Foreign Key
    model_id: int = Field(foreign_key="models.id", index=True)

    # Relationship
    model: "Model" = Relationship(back_populates="use_cases")


class UseCaseCreate(UseCaseBase):
    """Schema for creating a new use case via API"""
    model_id: int


class UseCaseUpdate(SQLModel):
    """Schema for updating a use case via API (all fields optional)"""
    use_case: str | None = None
    description: str | None = None
    mentioned_by: str | None = None


class UseCaseResponse(UseCaseBase):
    """Schema for use case in API responses"""
    id: int
    model_id: int
    created_at: datetime
    updated_at: datetime
```

**Let's break down the key SQLModel concepts:**

### 1. Field() Configuration

```python
name: str = Field(max_length=255, index=True, unique=True)
```

- `max_length`: Sets VARCHAR length
- `index=True`: Creates database index
- `unique=True`: Adds unique constraint
- `default=None`: Column is nullable

### 2. sa_column for Advanced Features

```python
description: str | None = Field(default=None, sa_column=Column(Text))
```

When SQLModel's `Field()` doesn't support a feature, use `sa_column` to pass a SQLAlchemy `Column` directly.

### 3. Foreign Keys

```python
model_id: int = Field(foreign_key="models.id", index=True)
```

Creates a foreign key constraint and indexes it for performance.

### 4. Relationships

```python
model: "Model" = Relationship(back_populates="benchmark_results")
```

**Important:** This is NOT a database column. It's SQLAlchemy magic that lets you access related objects:

```python
result = session.get(BenchmarkResult, 1)
print(result.model.name)  # Automatically loads related model
```

### 5. Table Configuration

```python
__table_args__ = (
    UniqueConstraint("model_id", "benchmark_id", "date_tested"),
    Index("ix_benchmark_results_model_benchmark", "model_id", "benchmark_id"),
)
```

For constraints and indexes that span multiple columns.

### 6. Modern Type Hints

```python
id: int | None = Field(default=None, primary_key=True)
```

We use Python 3.10+ union syntax (`int | None`) instead of `Optional[int]`. Cleaner and more modern!

### Update the Models Package

Edit `backend/app/models/__init__.py`:

```python
"""
Database models package
"""
from .base import TimestampMixin
from .models import (
    # Model entity
    Model, ModelBase, ModelCreate, ModelUpdate, ModelResponse,
    # Benchmark entity
    Benchmark, BenchmarkBase, BenchmarkCreate, BenchmarkUpdate, BenchmarkResponse,
    # BenchmarkResult entity
    BenchmarkResult, BenchmarkResultBase, BenchmarkResultCreate,
    BenchmarkResultUpdate, BenchmarkResultResponse,
    # Opinion entity
    Opinion, OpinionBase, OpinionCreate, OpinionUpdate, OpinionResponse,
    # UseCase entity
    UseCase, UseCaseBase, UseCaseCreate, UseCaseUpdate, UseCaseResponse,
)

__all__ = [
    # Base
    "TimestampMixin",
    # Models
    "Model", "ModelBase", "ModelCreate", "ModelUpdate", "ModelResponse",
    # Benchmarks
    "Benchmark", "BenchmarkBase", "BenchmarkCreate", "BenchmarkUpdate", "BenchmarkResponse",
    # BenchmarkResults
    "BenchmarkResult", "BenchmarkResultBase", "BenchmarkResultCreate",
    "BenchmarkResultUpdate", "BenchmarkResultResponse",
    # Opinions
    "Opinion", "OpinionBase", "OpinionCreate", "OpinionUpdate", "OpinionResponse",
    # UseCases
    "UseCase", "UseCaseBase", "UseCaseCreate", "UseCaseUpdate", "UseCaseResponse",
]
```

**🎯 Checkpoint:** Verify the models can be imported:

```bash
cd backend
uv run python -c "from app.models import Model, Benchmark; print('Models imported successfully!')"
cd ..
```

---

## Step 5: Installing and Configuring Alembic

**Alembic** is a database migration tool for SQLAlchemy. Think of it as "Git for your database schema." It lets you:

- Version control your schema changes
- Apply changes incrementally
- Rollback if something goes wrong
- Keep development and production databases in sync

### Initialize Alembic

```bash
cd backend

# Initialize Alembic
uv run alembic init alembic

cd ..
```

This creates:

- `backend/alembic/` directory with migration scripts
- `backend/alembic.ini` configuration file

### Configure Alembic for Async Operations

Edit `backend/alembic.ini` and find the line starting with `sqlalchemy.url`. **Comment it out** (we'll use the .env instead):

```ini
# sqlalchemy.url = driver://user:pass@localhost/dbname
```

Now edit `backend/alembic/env.py` to load the database URL from your `.env` file. Replace the entire file with:

```python
"""
Alembic Environment Configuration for SQLModel + Async
Loads database URL from environment variables for security
"""
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context
import asyncio
import sys
import os

# Add the parent directory to the path so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Import your app's configuration
from app.config import settings

# Import SQLModel for metadata
from sqlmodel import SQLModel

# Import all models so Alembic can detect them
# This import will trigger table creation in metadata
from app.models import models

# Alembic Config object
config = context.config

# Interpret the config file for logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set the SQLAlchemy URL from environment (convert to async format)
config.set_main_option("sqlalchemy.url", settings.database_url_async)

# SQLModel's metadata (includes all table=True models)
target_metadata = SQLModel.metadata


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.

    This configures the context with just a URL and not an Engine,
    though an Engine is acceptable here as well. By skipping the Engine
    creation we don't even need a DBAPI to be available.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    """Helper function to run migrations with a connection"""
    context.configure(
        connection=connection,
        target_metadata=target_metadata
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations():
    """Run migrations in async mode"""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode.

    In this scenario we need to create an Engine and associate a
    connection with the context.
    """
    asyncio.run(run_async_migrations())


# Determine which mode to run
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

**What did we just do?**

- Configured Alembic to work with **async SQLAlchemy**
- Imported `settings` from our app config (which loads `.env`)
- Set Alembic's database URL with the async driver (`postgresql+asyncpg://`)
- Set `target_metadata = SQLModel.metadata` so Alembic can detect our SQLModel tables
- Created async migration runner using `asyncio`

**🎯 Checkpoint:** Verify Alembic can connect:

```bash
cd backend
uv run alembic current
cd ..
```

You should see something like:

```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
```

(No errors = success! The "current" revision is empty because we haven't created migrations yet.)

---

## Step 6: Creating the Initial Migration

Now for the magic: Alembic will look at our SQLModel models and auto-generate SQL to create the tables!

```bash
cd backend

# Create the migration
uv run alembic revision --autogenerate -m "Initial schema: models, benchmarks, results, opinions, use cases"

cd ..
```

**What just happened?**

Alembic compared your models against the (empty) database and generated a migration file in `backend/alembic/versions/`. The filename will be something like `xxxx_initial_schema.py` where `xxxx` is a revision hash.

Let's examine the migration file:

```bash
# Find the migration file
ls backend/alembic/versions/
```

Open the migration file. You'll see two functions:

1. **`upgrade()`**: Runs when applying the migration (creates tables)
2. **`downgrade()`**: Runs when rolling back (drops tables)

Here's what the generated migration looks like (simplified):

```python
"""Initial schema: models, benchmarks, results, opinions, use cases

Revision ID: xxxx
Revises:
Create Date: 2025-xx-xx
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade() -> None:
    # Create models table
    op.create_table('models',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('organization', sa.String(length=255), nullable=False),
        sa.Column('release_date', sa.Date(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('license', sa.String(length=255), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_models_name'), 'models', ['name'], unique=False)

    # Create benchmarks table
    # ... (similar structure)

    # Create benchmark_results table with foreign keys
    # ... (includes ForeignKey constraints to models and benchmarks)

    # ... and so on for opinions and use_cases

def downgrade() -> None:
    # Drop tables in reverse order (respecting foreign key dependencies)
    op.drop_table('use_cases')
    op.drop_table('opinions')
    op.drop_table('benchmark_results')
    op.drop_table('benchmarks')
    op.drop_table('models')
```

**Why review the migration?** Auto-generation is great, but not perfect. Always review migrations before applying them, especially in production. Check for:

- Missing indexes on frequently queried columns
- Incorrect column types
- Missing constraints

For our learning project, the auto-generated migration should be perfect!

**🎯 Checkpoint:** You have a migration file in `backend/alembic/versions/`. Review it to understand what SQL will be executed.

---

## Step 7: Applying the Migration to Supabase

Time to create the tables in your Supabase database!

```bash
cd backend

# Apply the migration
uv run alembic upgrade head

cd ..
```

**What does this do?**

- Connects to your Supabase PostgreSQL database (using `DATABASE_URL` from `.env`)
- Runs all pending migrations (in this case, just the initial schema)
- Creates an `alembic_version` table to track which migrations have been applied

You should see output like:

```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> xxxx, Initial schema: models, benchmarks, results, opinions, use cases
```

**Success!** Your database schema is now live in Supabase.

**🎯 Checkpoint:** No errors during migration? Great! Let's verify the schema in the next step.

---

## Step 8: Verifying the Schema in Supabase Studio

Supabase provides a beautiful UI to inspect your database. Let's use it to verify everything worked.

1. Go to your Supabase project dashboard
2. Click **Table Editor** in the left sidebar
3. You should see your 5 tables:

   - `models`
   - `benchmarks`
   - `benchmark_results`
   - `opinions`
   - `use_cases`
   - `alembic_version` (Alembic's internal tracking table)

4. Click on the `models` table
5. Explore the structure

**What to verify:**

- ✅ All columns are present with correct types
- ✅ `name` has a unique constraint
- ✅ `id` is the primary key with auto-increment
- ✅ `created_at` and `updated_at` have default values
- ✅ `metadata` is JSONB type

6. Check `benchmark_results` table:

   - ✅ `model_id` and `benchmark_id` are foreign keys
   - ✅ Unique constraint on `(model_id, benchmark_id, date_tested)`

7. Check `opinions` table:
   - ✅ `tags` is an array type (`text[]`)

**Manual Testing:** Let's add some test data in Supabase Studio:

1. Go to **Table Editor** → `models`
2. Click **Insert** → **Insert row**
3. Fill in:
   - `name`: GPT-4
   - `organization`: OpenAI
   - `release_date`: 2023-03-14
   - `description`: Large multimodal model
4. Click **Save**

Now try querying it in the **SQL Editor**:

```sql
SELECT * FROM models WHERE name = 'GPT-4';
```

You should see your inserted row with auto-populated `id`, `created_at`, and `updated_at`!

**Clean up:** Delete the test row (we'll add data properly via the API in later modules).

**🎯 Checkpoint:** Tables exist in Supabase with the correct structure. You've successfully deployed your schema!

---

## Step 9: Writing Async Database Connection Tests

Let's write tests to ensure our application can connect to the database and the schema works correctly.

### Create Database Session Management

First, create `backend/app/db/session.py`:

```python
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import SQLModel
from app.config import settings
from typing import AsyncGenerator

# Create async engine
engine = create_async_engine(
    settings.database_url_async,
    echo=False,  # Set to True to see SQL queries (useful for debugging)
    future=True,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for FastAPI routes
    Provides a database session and ensures it's closed after use

    Usage in FastAPI:
        @app.get("/models")
        async def get_models(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        yield session


async def init_db():
    """
    Initialize database tables
    Only use in development - in production, use Alembic migrations
    """
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
```

Update `backend/app/db/__init__.py`:

```python
"""
Database utilities package
"""
from .session import get_db, AsyncSessionLocal, engine, init_db

__all__ = ["get_db", "AsyncSessionLocal", "engine", "init_db"]
```

### Create Test Fixtures

In order to test database interactions without affecting the real database, we'll create test fixtures that provide a fresh database session for each test.

Add the following two fixtures to `backend/tests/conftest.py`:

```python
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
                # (IntegrityError and other DB exceptions auto-rollback the transaction)
                if outer_tx.is_active:
                    await outer_tx.rollback()
```

### Create Database Tests

Create `backend/tests/test_database.py`:

```python
"""
Database connection and schema tests with SQLModel and Async SQLAlchemy
"""

import pytest
from sqlalchemy import text, inspect
from sqlmodel import select
from app.models.models import Model, Opinion


async def test_database_connection(test_session):
    """Test that we can connect to the database"""
    result = await test_session.exec(text("SELECT 1"))
    assert result.one() == (1,)


async def test_all_tables_exist(test_engine):
    """Test that all expected tables exist in the database"""
    expected_tables = [
        "models",
        "benchmarks",
        "benchmark_results",
        "opinions",
        "use_cases",
    ]
    async with test_engine.begin() as conn:
        # Check each expected table
        for table_name in expected_tables:
            result = await conn.run_sync(
                lambda sync_conn: inspect(sync_conn).has_table(table_name)
            )
            assert (
                result is True
            ), f"Table '{table_name}' does not exist in the database"


async def test_models_table_columns(test_engine):
    """Test that the 'models' table has the expected columns"""
    # Get columns
    async with test_engine.begin() as conn:
        columns = await conn.run_sync(
            lambda sync_conn: inspect(sync_conn).get_columns("models")
        )
        column_names = {col["name"] for col in columns}
        # Get column names from SQLModel definition
        model_fields = set()
        for name in Model.model_fields.keys():
            if name[-1] == "_":
                name = name[:-1]
            model_fields.add(name)
        assert set(column_names) == model_fields


async def test_can_create_model(test_session, sample_model):
    """Test that we can insert and query a model using SQLModel"""
    test_session.add(sample_model)
    await test_session.commit()  # OK: commits the SAVEPOINT, not the outer transaction
    await test_session.refresh(sample_model)

    # Verify it has an ID and created_at timestamp
    assert sample_model.id is not None, "Model ID should not be None after insert"
    assert sample_model.created_at is not None, "Model should have created_at timestamp"

    # Prove it was actually written by querying the DB
    stmt = select(Model).where(Model.id == sample_model.id)
    row = (await test_session.exec(stmt)).first()

    assert row.name == "gpt-test"
    assert row.display_name == "GPT Test Model"
    assert row.organization == "Test Org"


async def test_foreign_key_constraints(test_session, sample_model):
    """Test that foreign key relationships work correctly"""

    # Add the sample model first
    test_session.add(sample_model)
    await test_session.commit()
    await test_session.refresh(sample_model)

    # Create an opinion linked to the model
    test_opinion = Opinion(
        model_id=sample_model.id,
        content="This is a test opinion about the model.",
        author="Test User",
    )
    test_session.add(test_opinion)
    await test_session.commit()
    await test_session.refresh(test_opinion)

    # Verify forward relationship (Opinion -> Model)
    assert test_opinion.model.id == sample_model.id

    # Verify reverse relationship (Model -> Opinion)
    # Must specify attribute_names to eagerly load the relationship in async context
    await test_session.refresh(sample_model, attribute_names=["opinions"])
    assert len(sample_model.opinions) == 1
    assert sample_model.opinions[0].id == test_opinion.id


async def test_unique_constraint(test_session, sample_model):
    """Test that the unique constraint on model name is enforced"""
    from sqlalchemy.exc import IntegrityError

    # Add the sample model first
    test_session.add(sample_model)
    await test_session.commit()

    # Attempt to add another model with the same name
    duplicate_model = Model(
        name=sample_model.name,
        display_name="Another Model",
        organization="Another Org",
    )
    test_session.add(duplicate_model)

    with pytest.raises(IntegrityError) as exc_info:
        await test_session.commit()
    assert "unique constraint" in str(exc_info.value).lower()


async def test_jsonb_column(test_session, sample_model):
    """Test that JSONB columns work correctly"""
    from sqlalchemy.dialects.postgresql import JSONB

    metadata = {
        "pricing": "free",
        "context_window": 2048,
        "capabilities": ["text-generation", "code-completion"],
    }

    sample_model.metadata_ = metadata

    test_session.add(sample_model)
    await test_session.commit()
    await test_session.refresh(sample_model)

    # Verify the metadata was stored and retrieved correctly
    assert sample_model.metadata_ == metadata


async def test_cascade_delete(test_session, sample_model):
    """Test that cascade delete works for related opinions"""
    # Add the sample model first
    test_session.add(sample_model)
    await test_session.commit()
    await test_session.refresh(sample_model)

    # Create an opinion linked to the model
    test_opinion = Opinion(
        model_id=sample_model.id,
        content="This is a test opinion about the model.",
        author="Test User",
    )
    test_session.add(test_opinion)
    await test_session.commit()
    await test_session.refresh(test_opinion)

    # Verify the opinion exists
    stmt = select(Opinion).where(Opinion.id == test_opinion.id)
    row = (await test_session.exec(stmt)).first()
    assert row is not None

    # Delete the model
    await test_session.delete(sample_model)
    await test_session.commit()

    # Verify the opinion was also deleted
    stmt = select(Opinion).where(Opinion.id == test_opinion.id)
    row = (await test_session.exec(stmt)).first()
    assert row is None

```

### Run the Tests

```bash
cd backend
uv run pytest tests/test_database.py -v
cd ..
```

You should see all tests pass! 🎉

```
tests/test_database.py::test_database_connection PASSED
tests/test_database.py::test_all_tables_exist PASSED
tests/test_database.py::test_models_table_columns PASSED
tests/test_database.py::test_can_create_model PASSED
tests/test_database.py::test_foreign_key_constraints PASSED
tests/test_database.py::test_unique_constraint PASSED
tests/test_database.py::test_jsonb_column PASSED
tests/test_database.py::test_cascade_delete PASSED

====== 8 passed in X.XX s ======
```

**What do these tests verify?**

1. ✅ Database connection works
2. ✅ Tables were created correctly
3. ✅ We can insert and query data with SQLModel
4. ✅ Foreign key relationships work
5. ✅ Unique constraints are enforced
6. ✅ JSONB and array columns work correctly
7. ✅ CASCADE delete works as expected

**🎯 Final Checkpoint:** All database tests pass. Your SQLModel schema is production-ready!

---

## Understanding SQLModel's Query Patterns

Now that we have models and tests, let's understand how to query with SQLModel.

### The SQLModel select() Function

SQLModel uses SQLAlchemy's 2.0 style with the `select()` function:

```python
from sqlmodel import select

# Simple select
statement = select(Model).where(Model.name == "GPT-4")
result = await session.execute(statement)
model = result.scalar_one()

# Select with joins
statement = (
    select(Model, BenchmarkResult)
    .join(BenchmarkResult)
    .where(Model.name == "GPT-4")
)
result = await session.execute(statement)
rows = result.all()

# Count
statement = select(func.count()).select_from(Model)
result = await session.execute(statement)
count = result.scalar()
```

### Accessing Relationships

With SQLModel, relationships work like SQLAlchemy:

```python
# Get a model
model = await session.get(Model, 1)

# Access relationships (may require eager loading in async)
# Use selectinload or joinedload for efficient loading
from sqlalchemy.orm import selectinload

statement = (
    select(Model)
    .where(Model.id == 1)
    .options(selectinload(Model.benchmark_results))
)
result = await session.execute(statement)
model = result.scalar_one()

# Now you can access the relationship
for result in model.benchmark_results:
    print(result.score)
```

---

## Understanding Indexing Strategy

You might have noticed we added indexes to certain columns. Let's understand why.

### What is an Index?

An index is like a book's index—it helps find information quickly without reading every page. In databases:

- **Without index:** Database scans every row to find matches (slow for large tables)
- **With index:** Database uses a data structure (usually B-tree) to jump directly to matches (fast!)

### When to Add Indexes

**Index these columns:**

1. **Primary keys** (automatic in PostgreSQL)
2. **Foreign keys** (we did this with `index=True`)
3. **Columns frequently used in WHERE clauses** (we did this: `name`, `category`)
4. **Columns used in ORDER BY** (we did this: `date_published`)
5. **Columns in unique constraints** (automatic)

**Don't over-index:**

- Indexes speed up reads but slow down writes (every INSERT/UPDATE must update the index)
- Indexes take disk space
- Too many indexes can confuse the query planner

**Our indexing strategy:**

```python
# Examples from our models:

# Frequently searched by name
name: str = Field(max_length=255, index=True, unique=True)

# Foreign keys for join performance
model_id: int = Field(foreign_key="models.id", index=True)

# Composite index for common query pattern
__table_args__ = (
    Index("ix_benchmark_results_model_benchmark", "model_id", "benchmark_id"),
)
```

**Query example that benefits from our indexes:**

```sql
-- Fast because we indexed model_id and benchmark_id
SELECT * FROM benchmark_results
WHERE model_id = 1 AND benchmark_id = 5;

-- Fast because we indexed models.name
SELECT * FROM models WHERE name = 'GPT-4';
```

---

## Key Design Decisions Explained

Let's reflect on the "why" behind our design choices.

### Decision 1: Why SQLModel Over Plain SQLAlchemy?

**Alternative:** Use SQLAlchemy + Pydantic separately.

**Why we chose SQLModel:**

- **Single source of truth**: Define fields once
- **Better FastAPI integration**: Created by the same author
- **Type safety**: Full editor support with type hints
- **Less code**: No duplication between ORM and schemas
- **Same power**: SQLAlchemy features still available when needed

**When to use plain SQLAlchemy:**

- Very complex legacy schemas that don't map well to Pydantic
- Need features not yet supported by SQLModel (rare)
- Team already has deep SQLAlchemy expertise

### Decision 2: Why JSONB for Metadata Instead of Columns?

**Alternative:** Add columns for every possible attribute:

```python
context_window: int | None = None
multimodal: bool | None = None
pricing_input: float | None = None
pricing_output: float | None = None
# ... 50 more columns
```

**Why we didn't:**

- Different models have different attributes
- New models introduce new attributes
- Schema changes are expensive in production
- Most columns would be NULL for most models

**Our approach:** JSONB column for flexible metadata

- Schema-less storage for variable attributes
- Still queryable with PostgreSQL's JSON operators
- Easy to add new fields without migration
- Perfect for "unknown unknowns"

**When to use JSONB:**

- Data structure varies by row
- Attributes are optional and numerous
- You need flexibility over rigid structure

**When NOT to use JSONB:**

- Data you'll frequently filter/sort by (use columns instead)
- Data with strict validation requirements
- Relationships to other tables (use foreign keys)

### Decision 3: Why CASCADE Delete?

```python
model_id: int = Field(foreign_key="models.id", index=True)

# In relationship:
sa_relationship_kwargs={"cascade": "all, delete-orphan"}
```

**What does CASCADE do?**

When you delete a model, automatically delete all related benchmark results, opinions, and use cases.

**Alternative:** `RESTRICT` or `SET NULL`

- `RESTRICT`: Prevent deletion if related rows exist (must delete children first)
- `SET NULL`: Set foreign key to NULL when parent is deleted (orphans the child)

**Why CASCADE for this project:**

- If we delete a model, its results/opinions are meaningless
- Prevents "orphaned" data
- Simpler application logic (no need to manually delete children)

**When NOT to use CASCADE:**

- When child data should survive parent deletion (e.g., deleting a user shouldn't delete their comments)
- When you need audit trails

### Decision 4: Why Timestamps on Every Table?

```python
class TimestampMixin(SQLModel):
    created_at: datetime | None = Field(...)
    updated_at: datetime | None = Field(...)
```

**Benefits:**

- Debugging: "When was this added?"
- Auditing: "What changed recently?"
- Analytics: "How much data do we get per day?"
- Data quality: "This benchmark result is 2 years old—is it still relevant?"

**Cost:** 16 bytes per row (negligible for most applications)

**Professional practice:** Always include timestamps. You'll thank yourself later.

---

## What You've Accomplished

Congratulations! 🎉 You've designed and deployed a production-ready database schema using modern SQLModel. Here's what you now have:

1. **Solid Database Design Skills**

   - Understanding of normalization and when to apply it
   - Knowledge of foreign keys, indexes, and constraints
   - Ability to model relationships between entities

2. **SQLModel Mastery**

   - Unified models that serve as both tables and schemas
   - Type-safe, validated data models
   - Understanding of base models, table models, and schema models
   - Knowledge of when to use `Field()` vs `sa_column()`

3. **Supabase PostgreSQL Database**

   - Managed database with automatic backups
   - Beautiful UI for inspection and testing
   - Production-ready infrastructure

4. **Five Core Tables**

   - `models` - AI models with flexible metadata
   - `benchmarks` - Academic benchmarks
   - `benchmark_results` - Performance scores
   - `opinions` - Public sentiment and feedback
   - `use_cases` - Mentioned use cases

5. **Alembic Migration System**

   - Version control for database schema
   - Ability to evolve schema safely
   - Rollback capability if things go wrong
   - Async-compatible configuration

6. **Comprehensive Test Coverage**
   - Connection tests
   - Schema validation
   - Constraint enforcement
   - JSONB and array functionality
   - Cascade delete behavior

### Key Takeaways

- **SQLModel unifies ORM and schemas** - define fields once, use everywhere
- **Normalization prevents data inconsistency** by storing each fact once
- **Foreign keys enforce referential integrity** at the database level
- **Indexes are essential for query performance** on large datasets
- **JSONB provides flexibility** when your data structure varies
- **Migrations are version control for your schema** and essential for teams
- **Constraints are your safety net** - they prevent invalid data
- **Async operations are the future** of Python database access

---

## What's Next?

In **Module 1.2: Repository Pattern with SQLModel**, you'll:

- Implement the **Repository Pattern** to abstract database operations
- Create a `BaseRepository` with async CRUD operations using SQLModel
- Build specific repositories for each entity (`ModelRepository`, `BenchmarkRepository`, etc.)
- Learn **dependency injection** patterns for FastAPI
- Write comprehensive unit tests for repository methods
- Understand **session management** and async context managers
- Use SQLModel's `select()` for type-safe queries

You've built the schema with SQLModel. Now it's time to build the layer that interacts with it!

---

## Additional Resources

### SQLModel

- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [SQLModel GitHub](https://github.com/tiangolo/sqlmodel)
- [FastAPI with SQLModel Tutorial](https://sqlmodel.tiangolo.com/tutorial/fastapi/)

### Database Design

- [Database Normalization Explained](https://www.guru99.com/database-normalization.html)
- [PostgreSQL Tutorial](https://www.postgresqltutorial.com/)
- [When to Use JSONB in PostgreSQL](https://www.postgresql.org/docs/current/datatype-json.html)

### Alembic

- [Alembic Tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
- [Auto Generating Migrations](https://alembic.sqlalchemy.org/en/latest/autogenerate.html)

### SQLAlchemy 2.0

- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/en/20/)
- [Async SQLAlchemy Guide](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)

### Supabase

- [Supabase Documentation](https://supabase.com/docs)
- [PostgreSQL in Supabase](https://supabase.com/docs/guides/database/overview)

---

**Next Module:** [Module 1.2 - Repository Pattern with SQLModel](./module-1.2-repository-pattern.md)

---
