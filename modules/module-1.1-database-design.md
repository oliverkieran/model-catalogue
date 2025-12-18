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

Most importantly, you'll learn to think in terms of **data integrity**—ensuring your database can't get into an invalid state, even when things go wrong.

This isn't just theory. You'll create a real database on Supabase (managed PostgreSQL), design a production-ready schema for the AI Model Catalogue, and write your first database migration.

---

## What You'll Build

By the end of this module, you'll have:

- ✅ A Supabase project with PostgreSQL database
- ✅ Understanding of database normalization and when to use it
- ✅ Complete schema design for 5 core entities (Models, Benchmarks, Results, Opinions, UseCases)
- ✅ Alembic configured for database migrations
- ✅ Initial migration creating all tables with proper constraints
- ✅ Schema deployed to Supabase and verified
- ✅ Database connection tests to validate setup

---

## Step 1: Understanding Relational Database Design

Before we write any SQL, let's understand the principles that will guide our decisions.

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
| id | name   | organization |
|----|--------|--------------|
| 1  | GPT-4  | OpenAI       |
| 2  | Claude 3 | Anthropic |

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

1. Click on the **Connect** tab in the project's navigation bar
2. Select Type: URI, and Method: Direct connection
3. Copy the **URI** connection string (should look like):

```
postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
```

4. Replace `[YOUR-PASSWORD]` with the database password you set earlier

### Update Your .env File

Open your `.env` file and update the `DATABASE_URL`:

```bash
# .env
DATABASE_URL=postgresql://postgres:your-actual-password@db.xxxxx.supabase.co:5432/postgres
```

**Security Note:** The `.env` file is in `.gitignore` and will NEVER be committed to version control. Anyone with this URL can access your database—treat it like a password!

**🎯 Checkpoint:** Your `DATABASE_URL` environment variable is set. We'll test the connection in a later step.

---

## Step 4: Installing and Configuring Alembic

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

### Configure Alembic to Use Your Database

Edit `backend/alembic.ini` and find the line starting with `sqlalchemy.url`. **Comment it out** (we'll use the .env instead):

```ini
# sqlalchemy.url = driver://user:pass@localhost/dbname
```

Now edit `backend/alembic/env.py` to load the database URL from your `.env` file. Replace the entire file with:

```python
"""
Alembic Environment Configuration
Loads database URL from environment variables for security
"""
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import sys
import os

# Add the parent directory to the path so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Import your app's configuration
from app.config import settings

# Import all models so Alembic can detect them
# (We'll create these in Module 1.2, but import statement is ready)
# from app.models import Base

# Alembic Config object
config = context.config

# Interpret the config file for logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set the SQLAlchemy URL from environment
config.set_main_option("sqlalchemy.url", settings.database_url)

# Add your model's MetaData object here for 'autogenerate' support
# target_metadata = Base.metadata
target_metadata = None  # We'll update this in Module 1.2


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


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode.

    In this scenario we need to create an Engine and associate a
    connection with the context.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


# Determine which mode to run
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

**What did we just do?**

- Imported `settings` from our app config (which loads `.env`)
- Set Alembic's database URL from `settings.database_url`
- Prepared the file to detect our models (we'll add those in Module 1.2)

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

## Step 5: Creating SQLAlchemy Models

Before we can auto-generate migrations, we need to define our SQLAlchemy models. These are Python classes that represent database tables.

Create `backend/app/models/base.py` for the base configuration:

```python
"""
SQLAlchemy Base Configuration
All models inherit from this Base class
"""
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import DateTime, func
from datetime import datetime


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy models
    Provides common functionality like timestamps
    """
    pass


class TimestampMixin:
    """
    Mixin that adds created_at and updated_at timestamps to models
    """
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
```

**Why a mixin?** We'll add `created_at` and `updated_at` to every table. Rather than copy-pasting, we use a mixin—a reusable component that we can "mix in" to any model.

Now create the models file `backend/app/models/models.py`:

```python
"""
Database Models for AI Model Catalogue

These SQLAlchemy models define the database schema.
Alembic will auto-generate migrations from these definitions.
"""
from sqlalchemy import String, Integer, Float, Text, Date, ARRAY, Index, UniqueConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB
from typing import Optional, List
from datetime import date, datetime

from .base import Base, TimestampMixin


class Model(Base, TimestampMixin):
    """
    Represents an AI model (e.g., GPT-4, Claude, Llama)
    """
    __tablename__ = "models"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    organization: Mapped[str] = mapped_column(String(255), nullable=False)
    release_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # JSONB for flexible metadata (pricing, context_window, capabilities, etc.)
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Relationships (we'll use these in queries later)
    benchmark_results: Mapped[List["BenchmarkResult"]] = relationship(
        "BenchmarkResult", back_populates="model", cascade="all, delete-orphan"
    )
    opinions: Mapped[List["Opinion"]] = relationship(
        "Opinion", back_populates="model", cascade="all, delete-orphan"
    )
    use_cases: Mapped[List["UseCase"]] = relationship(
        "UseCase", back_populates="model", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Model(id={self.id}, name='{self.name}', organization='{self.organization}')>"


class Benchmark(Base, TimestampMixin):
    """
    Represents an academic benchmark used to evaluate AI models
    """
    __tablename__ = "benchmarks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Relationships
    results: Mapped[List["BenchmarkResult"]] = relationship(
        "BenchmarkResult", back_populates="benchmark", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Benchmark(id={self.id}, name='{self.name}', category='{self.category}')>"


class BenchmarkResult(Base, TimestampMixin):
    """
    Represents a model's performance on a specific benchmark
    This is the "join table" between Models and Benchmarks, with extra data (score, date, source)
    """
    __tablename__ = "benchmark_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Foreign Keys
    model_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("models.id", ondelete="CASCADE"), nullable=False, index=True
    )
    benchmark_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("benchmarks.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Result data
    score: Mapped[float] = mapped_column(Float, nullable=False)
    date_tested: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    source: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Relationships
    model: Mapped["Model"] = relationship("Model", back_populates="benchmark_results")
    benchmark: Mapped["Benchmark"] = relationship("Benchmark", back_populates="results")

    # Constraints
    __table_args__ = (
        # Prevent duplicate results for the same model+benchmark on the same date
        UniqueConstraint("model_id", "benchmark_id", "date_tested", name="uix_model_benchmark_date"),
        # Composite index for common queries
        Index("ix_benchmark_results_model_benchmark", "model_id", "benchmark_id"),
    )

    def __repr__(self):
        return f"<BenchmarkResult(model_id={self.model_id}, benchmark_id={self.benchmark_id}, score={self.score})>"


class Opinion(Base, TimestampMixin):
    """
    Represents public opinion about a model from various sources
    """
    __tablename__ = "opinions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Foreign Key
    model_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("models.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Opinion data
    content: Mapped[str] = mapped_column(Text, nullable=False)
    sentiment: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    source: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    author: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    date_published: Mapped[Optional[date]] = mapped_column(Date, nullable=True, index=True)

    # PostgreSQL array for tags (e.g., ["coding", "creative-writing"])
    tags: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)

    # Relationship
    model: Mapped["Model"] = relationship("Model", back_populates="opinions")

    def __repr__(self):
        return f"<Opinion(id={self.id}, model_id={self.model_id}, sentiment='{self.sentiment}')>"


class UseCase(Base, TimestampMixin):
    """
    Represents a mentioned use case for a model
    """
    __tablename__ = "use_cases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Foreign Key
    model_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("models.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Use case data
    use_case: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    mentioned_by: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Relationship
    model: Mapped["Model"] = relationship("Model", back_populates="use_cases")

    def __repr__(self):
        return f"<UseCase(id={self.id}, model_id={self.model_id}, use_case='{self.use_case}')>"
```

**Let's break down the key concepts:**

1. **`Mapped[type]`**: SQLAlchemy 2.0's type hint system. It tells both Python and SQLAlchemy what type each column is.

2. **`mapped_column(...)`**: Defines how the column is configured in the database.

3. **`ForeignKey(..., ondelete="CASCADE")`**: When a model is deleted, automatically delete all related benchmark results, opinions, and use cases. This prevents "orphaned" data.

4. **`relationship(...)`**: Not a database column! This is SQLAlchemy's way of letting you access related objects in Python:

   ```python
   model = session.get(Model, 1)
   print(model.benchmark_results)  # Returns all results for this model
   ```

5. **`Index(...)`**: Creates database indexes for faster queries. We index foreign keys and frequently searched columns (name, category, date_published).

6. **`UniqueConstraint(...)`**: Prevents duplicate data. You can't insert the same model+benchmark+date twice.

7. **`JSONB`**: PostgreSQL's JSON type with indexing and query support. Perfect for flexible metadata.

8. **`ARRAY(String)`**: PostgreSQL array type. Perfect for simple lists like tags.

### Update the models package

Edit `backend/app/models/__init__.py` to export all models:

```python
"""
Database models package
"""
from .base import Base, TimestampMixin
from .models import Model, Benchmark, BenchmarkResult, Opinion, UseCase

__all__ = [
    "Base",
    "TimestampMixin",
    "Model",
    "Benchmark",
    "BenchmarkResult",
    "Opinion",
    "UseCase",
]
```

Now update `backend/alembic/env.py` to import the models. Find this line:

```python
target_metadata = None  # We'll update this in Module 1.2
```

Replace it with:

```python
# Import models so Alembic can detect schema changes
from app.models import Base
target_metadata = Base.metadata
```

**🎯 Checkpoint:** Verify the models can be imported:

```bash
cd backend
uv run python -c "from app.models import Model, Benchmark; print('Models imported successfully!')"
cd ..
```

---

## Step 6: Creating the Initial Migration

Now for the magic: Alembic will look at our models and auto-generate SQL to create the tables!

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
# Find the migration file (it'll be in backend/alembic/versions/)
cd backend
ls alembic/versions/
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
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('organization', sa.String(length=255), nullable=False),
        sa.Column('release_date', sa.Date(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_models_name'), 'models', ['name'], unique=False)

    # Create benchmarks table
    # ... (similar to models)

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
5. Click the **⚙ Definition** tab (or similar) to see the schema

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
   - ✅ `tags` is an array type

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

## Step 9: Writing Database Connection Tests

Let's write tests to ensure our application can connect to the database and the schema is correct.

First, create a database utility file `backend/app/db/session.py`:

```python
"""
Database session management
Provides async session factory for database operations
"""
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.config import settings
from typing import AsyncGenerator

# Convert the Supabase URL to async format (postgresql+asyncpg://)
database_url = settings.database_url.replace("postgresql://", "postgresql+asyncpg://")

# Create async engine
engine = create_async_engine(
    database_url,
    echo=False,  # Set to True to see SQL queries (useful for debugging)
    future=True,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
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
        try:
            yield session
        finally:
            await session.close()
```

**Why async?** FastAPI is async-first. Using async database sessions prevents blocking the event loop during database I/O.

Now update `backend/app/db/__init__.py`:

```python
"""
Database utilities package
"""
from .session import get_db, AsyncSessionLocal, engine

__all__ = ["get_db", "AsyncSessionLocal", "engine"]
```

### Add asyncpg Dependency

We need the async PostgreSQL driver:

```bash
cd backend
uv add asyncpg
cd ..
```

### Create Database Tests

Create `backend/tests/test_database.py`:

```python
"""
Database connection and schema tests
"""
import pytest
from sqlalchemy import text, inspect
from app.db import engine, AsyncSessionLocal
from app.models import Model, Benchmark, BenchmarkResult, Opinion, UseCase


@pytest.mark.asyncio
async def test_database_connection():
    """Test that we can connect to the database"""
    async with AsyncSessionLocal() as session:
        result = await session.execute(text("SELECT 1"))
        assert result.scalar() == 1


@pytest.mark.asyncio
async def test_models_table_exists():
    """Test that the models table was created with correct columns"""
    async with engine.begin() as conn:
        # Get table schema
        result = await conn.run_sync(
            lambda sync_conn: inspect(sync_conn).has_table("models")
        )
        assert result is True


@pytest.mark.asyncio
async def test_benchmarks_table_exists():
    """Test that the benchmarks table exists"""
    async with engine.begin() as conn:
        result = await conn.run_sync(
            lambda sync_conn: inspect(sync_conn).has_table("benchmarks")
        )
        assert result is True


@pytest.mark.asyncio
async def test_can_create_model():
    """Test that we can insert and query a model"""
    async with AsyncSessionLocal() as session:
        # Create a test model
        test_model = Model(
            name="Test-Model-12345",
            organization="Test Org",
            description="A test model for database testing"
        )

        session.add(test_model)
        await session.commit()
        await session.refresh(test_model)

        # Verify it has an ID
        assert test_model.id is not None
        assert test_model.created_at is not None
        assert test_model.updated_at is not None

        # Clean up - delete the test model
        await session.delete(test_model)
        await session.commit()


@pytest.mark.asyncio
async def test_foreign_key_relationship():
    """Test that foreign key relationships work correctly"""
    async with AsyncSessionLocal() as session:
        # Create a model
        test_model = Model(
            name="FK-Test-Model-67890",
            organization="Test Org"
        )
        session.add(test_model)
        await session.commit()
        await session.refresh(test_model)

        # Create a benchmark
        test_benchmark = Benchmark(
            name="FK-Test-Benchmark-67890",
            category="Testing"
        )
        session.add(test_benchmark)
        await session.commit()
        await session.refresh(test_benchmark)

        # Create a benchmark result linking them
        test_result = BenchmarkResult(
            model_id=test_model.id,
            benchmark_id=test_benchmark.id,
            score=95.5
        )
        session.add(test_result)
        await session.commit()
        await session.refresh(test_result)

        # Verify the relationship
        assert test_result.model_id == test_model.id
        assert test_result.benchmark_id == test_benchmark.id
        assert test_result.score == 95.5

        # Clean up
        await session.delete(test_result)
        await session.delete(test_benchmark)
        await session.delete(test_model)
        await session.commit()


@pytest.mark.asyncio
async def test_unique_constraint():
    """Test that unique constraints are enforced"""
    from sqlalchemy.exc import IntegrityError

    async with AsyncSessionLocal() as session:
        # Create a model
        model1 = Model(name="Unique-Test-99999", organization="Test Org")
        session.add(model1)
        await session.commit()

        # Try to create another model with the same name (should fail)
        model2 = Model(name="Unique-Test-99999", organization="Another Org")
        session.add(model2)

        with pytest.raises(IntegrityError):
            await session.commit()

        # Rollback the failed transaction
        await session.rollback()

        # Clean up the first model
        await session.delete(model1)
        await session.commit()


@pytest.mark.asyncio
async def test_jsonb_and_array_columns():
    """Test that JSONB and ARRAY columns work correctly"""
    async with AsyncSessionLocal() as session:
        # Create a model with JSONB metadata
        test_model = Model(
            name="JSONB-Test-11111",
            organization="Test Org",
            metadata={
                "context_window": 128000,
                "multimodal": True,
                "pricing": {"input": 0.03, "output": 0.06}
            }
        )
        session.add(test_model)
        await session.commit()
        await session.refresh(test_model)

        # Create an opinion with array tags
        test_opinion = Opinion(
            model_id=test_model.id,
            content="This model is great for testing!",
            sentiment="positive",
            tags=["testing", "example", "demo"]
        )
        session.add(test_opinion)
        await session.commit()
        await session.refresh(test_opinion)

        # Verify JSONB and array data
        assert test_model.metadata["context_window"] == 128000
        assert test_model.metadata["multimodal"] is True
        assert test_opinion.tags == ["testing", "example", "demo"]

        # Clean up
        await session.delete(test_opinion)
        await session.delete(test_model)
        await session.commit()
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
tests/test_database.py::test_models_table_exists PASSED
tests/test_database.py::test_benchmarks_table_exists PASSED
tests/test_database.py::test_can_create_model PASSED
tests/test_database.py::test_foreign_key_relationship PASSED
tests/test_database.py::test_unique_constraint PASSED
tests/test_database.py::test_jsonb_and_array_columns PASSED

====== 7 passed in X.XX s ======
```

**What do these tests verify?**

1. ✅ Database connection works
2. ✅ Tables were created correctly
3. ✅ We can insert and query data
4. ✅ Foreign key relationships work
5. ✅ Unique constraints are enforced
6. ✅ JSONB and array columns work correctly

**🎯 Final Checkpoint:** All database tests pass. Your schema is production-ready!

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
2. **Foreign keys** (we did this: `model_id`, `benchmark_id`)
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
name: Mapped[str] = mapped_column(String(255), unique=True, index=True)

# Foreign keys for join performance
model_id: Mapped[int] = mapped_column(
    Integer, ForeignKey("models.id"), nullable=False, index=True
)

# Composite index for common query pattern
Index("ix_benchmark_results_model_benchmark", "model_id", "benchmark_id")
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

## Common Pitfalls and How to Avoid Them

### Pitfall 1: Wrong Database URL Format

**Symptom:**

```
sqlalchemy.exc.ArgumentError: Could not parse rfc1738 URL from string
```

**Solution:** Ensure your `DATABASE_URL` uses the correct format:

```
postgresql://postgres:password@db.xxx.supabase.co:5432/postgres
```

Common mistakes:

- Missing `postgresql://` prefix
- Spaces in the password (URL-encode them as `%20`)
- Wrong port (should be `5432` for PostgreSQL)

### Pitfall 2: Forgetting to Install asyncpg

**Symptom:**

```
ModuleNotFoundError: No module named 'asyncpg'
```

**Solution:**

```bash
cd backend
uv add asyncpg
```

### Pitfall 3: Alembic Can't Find Models

**Symptom:** `alembic revision --autogenerate` generates an empty migration.

**Solution:** Ensure you imported `Base.metadata` in `alembic/env.py`:

```python
from app.models import Base
target_metadata = Base.metadata
```

### Pitfall 4: Migration Fails with Foreign Key Error

**Symptom:**

```
sqlalchemy.exc.IntegrityError: foreign key constraint fails
```

**Cause:** Tables created in wrong order (child before parent).

**Solution:** Alembic should handle this automatically. If not, manually reorder `create_table` calls in the migration file so parent tables are created first:

1. `models` and `benchmarks` (no dependencies)
2. `benchmark_results`, `opinions`, `use_cases` (depend on models)

### Pitfall 5: Tests Fail with Connection Timeout

**Symptom:** Tests hang and eventually timeout.

**Cause:** Database URL is incorrect or Supabase project is paused.

**Solution:**

1. Check your `.env` file has the correct `DATABASE_URL`
2. Go to Supabase dashboard—projects on the free tier pause after inactivity. Click to resume.
3. Verify connection manually:
   ```bash
   cd backend
   uv run python -c "from app.config import settings; print(settings.database_url)"
   ```

---

## Key Design Decisions Explained

Let's reflect on the "why" behind our design choices.

### Decision 1: Why Separate Tables Instead of One Big Table?

**Alternative:** Put everything in one table:

```
| id | name | org | benchmark | score | opinion | sentiment |
```

**Why we didn't:**

- Massive redundancy (model info repeated for every benchmark)
- Can't have a model without results, or results without opinions
- Difficult to query ("show me all benchmarks" requires finding unique values in a column)
- Violates normal forms (1NF, 2NF, 3NF)

**Our approach:** Normalized schema with relationships

- Each entity has its own table
- Relationships via foreign keys
- Query flexibility with JOINs

### Decision 2: Why JSONB for Metadata Instead of Columns?

**Alternative:** Add columns for every possible attribute:

```python
context_window: Mapped[Optional[int]]
multimodal: Mapped[Optional[bool]]
pricing_input: Mapped[Optional[float]]
pricing_output: Mapped[Optional[float]]
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
model_id: Mapped[int] = mapped_column(
    ForeignKey("models.id", ondelete="CASCADE")
)
```

**What does `ondelete="CASCADE"` do?**

When you delete a model, automatically delete all related benchmark results, opinions, and use cases.

**Alternative:** `ondelete="RESTRICT"` or `ondelete="SET NULL"`

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
created_at: Mapped[datetime] = mapped_column(server_default=func.now())
updated_at: Mapped[datetime] = mapped_column(onupdate=func.now())
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

Congratulations! 🎉 You've designed and deployed a production-ready database schema. Here's what you now have:

1. **Solid Database Design Skills**

   - Understanding of normalization and when to apply it
   - Knowledge of foreign keys, indexes, and constraints
   - Ability to model relationships between entities

2. **Supabase PostgreSQL Database**

   - Managed database with automatic backups
   - Beautiful UI for inspection and testing
   - Production-ready infrastructure

3. **Five Core Tables**

   - `models` - AI models with flexible metadata
   - `benchmarks` - Academic benchmarks
   - `benchmark_results` - Performance scores
   - `opinions` - Public sentiment and feedback
   - `use_cases` - Mentioned use cases

4. **Alembic Migration System**

   - Version control for database schema
   - Ability to evolve schema safely
   - Rollback capability if things go wrong

5. **Comprehensive Test Coverage**
   - Connection tests
   - Schema validation
   - Constraint enforcement
   - JSONB and array functionality

### Key Takeaways

- **Normalization prevents data inconsistency** by storing each fact once
- **Foreign keys enforce referential integrity** at the database level
- **Indexes are essential for query performance** on large datasets
- **JSONB provides flexibility** when your data structure varies
- **Migrations are version control for your schema** and essential for teams
- **Constraints are your safety net** - they prevent invalid data

---

## What's Next?

In **Module 1.2: SQLAlchemy Models & Repository Pattern**, you'll:

- Implement the **Repository Pattern** to abstract database operations
- Create a `BaseRepository` with CRUD operations (Create, Read, Update, Delete)
- Build specific repositories for each entity (`ModelRepository`, `BenchmarkRepository`, etc.)
- Learn **dependency injection** patterns for FastAPI
- Write comprehensive unit tests for repository methods
- Understand **session management** and async context managers

You've built the schema. Now it's time to build the layer that interacts with it!

---

## Troubleshooting

### Alembic Commands Hang

**Cause:** Can't connect to database.

**Solution:**

1. Check `.env` has correct `DATABASE_URL`
2. Test connection manually:
   ```bash
   cd backend
   uv run python -c "import asyncio; from app.db import engine; asyncio.run(engine.connect())"
   ```
3. Check Supabase project is running (not paused)

### "Table already exists" Error

**Cause:** You ran the migration twice, or created tables manually.

**Solution:**

```bash
cd backend
# Check current migration state
uv run alembic current

# If confused, downgrade and re-upgrade
uv run alembic downgrade base
uv run alembic upgrade head
```

### Import Errors in Tests

**Cause:** Missing dependencies or wrong Python path.

**Solution:**

```bash
cd backend
uv sync
uv run pytest tests/test_database.py -v
```

### Can't Connect from Local Machine

**Cause:** Supabase projects are accessible from anywhere by default, but check firewall.

**Solution:**

1. Go to Supabase Project Settings → Database
2. Ensure "Enable connection pooling" is ON
3. Use the "Session" mode connection string (not "Transaction")
4. If still failing, check your local firewall isn't blocking port 5432

### Tests Pass but Supabase Studio Shows No Data

**Cause:** Tests clean up after themselves (as they should!).

**Solution:** This is expected behavior. Tests insert and then delete data. To see data in Supabase Studio, manually insert via the UI or run the app (in future modules).

---

## Additional Resources

### Database Design

- [Database Normalization Explained](https://www.guru99.com/database-normalization.html)
- [PostgreSQL Tutorial](https://www.postgresqltutorial.com/)
- [When to Use JSONB in PostgreSQL](https://www.postgresql.org/docs/current/datatype-json.html)

### Alembic

- [Alembic Tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
- [Auto Generating Migrations](https://alembic.sqlalchemy.org/en/latest/autogenerate.html)

### SQLAlchemy

- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/en/20/)
- [Async SQLAlchemy Guide](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)

### Supabase

- [Supabase Documentation](https://supabase.com/docs)
- [PostgreSQL in Supabase](https://supabase.com/docs/guides/database/overview)

---

**Next Module:** [Module 1.2 - SQLAlchemy Models & Repository Pattern](./module-1.2-repository-pattern.md)

---

## Appendix: Common SQL Queries for This Schema

Once you have data in your database (in future modules), here are useful queries:

```sql
-- Get all models with their benchmark scores
SELECT m.name, m.organization, b.name as benchmark, br.score
FROM models m
JOIN benchmark_results br ON m.id = br.model_id
JOIN benchmarks b ON br.benchmark_id = b.id
ORDER BY m.name, b.name;

-- Find top-performing model on a specific benchmark
SELECT m.name, m.organization, br.score
FROM models m
JOIN benchmark_results br ON m.id = br.model_id
JOIN benchmarks b ON br.benchmark_id = b.id
WHERE b.name = 'MMLU'
ORDER BY br.score DESC
LIMIT 5;

-- Get all opinions for a model
SELECT o.content, o.sentiment, o.source, o.date_published
FROM opinions o
JOIN models m ON o.model_id = m.id
WHERE m.name = 'GPT-4'
ORDER BY o.date_published DESC;

-- Find models with specific metadata attribute
SELECT name, organization, metadata->>'context_window' as context_window
FROM models
WHERE metadata->>'multimodal' = 'true';

-- Count benchmark results per model
SELECT m.name, COUNT(br.id) as num_results
FROM models m
LEFT JOIN benchmark_results br ON m.id = br.model_id
GROUP BY m.id, m.name
ORDER BY num_results DESC;
```

Practice these queries in Supabase Studio's SQL Editor to get comfortable with your schema!
