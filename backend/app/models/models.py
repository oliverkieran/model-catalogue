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
from datetime import date, datetime

from .base import TimestampMixin


# =============================================================================
# Models Entity
# =============================================================================


class ModelBase(SQLModel):
    """Base model with shared fields for AI models"""

    name: str = Field(max_length=255, index=True, unique=True)
    display_name: str = Field(max_length=255)
    organization: str = Field(max_length=255)
    release_date: date | None = Field(default=None)
    description: str | None = Field(default=None, sa_column=Column(Text))
    license: str | None = Field(default=None, max_length=255)


class Model(ModelBase, TimestampMixin, table=True):
    """Database table for AI models"""

    __tablename__ = "models"

    id: int | None = Field(default=None, primary_key=True)

    # JSONB for flexible metadata (pricing, context_window, capabilities, etc.)
    # Using sa_column because SQLModel doesn't directly support JSONB
    metadata_: dict | None = Field(
        default=None, sa_column=Column("metadata", JSONB, nullable=True)
    )

    # Relationships
    benchmark_results: list["BenchmarkResult"] = Relationship(
        back_populates="model", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    opinions: list["Opinion"] = Relationship(
        back_populates="model", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    use_cases: list["UseCase"] = Relationship(
        back_populates="model", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )


class ModelCreate(ModelBase):
    """Pydantic schema for creating a new AI model via API"""

    metadata_: dict | None = None


class ModelUpdate(SQLModel):
    """Pydantic schema for updating an existing AI model via API"""

    name: str | None = Field(default=None, max_length=255)
    display_name: str | None = Field(default=None, max_length=255)
    organization: str | None = Field(default=None, max_length=255)
    release_date: date | None = None
    description: str | None = None
    license: str | None = Field(default=None, max_length=255)
    metadata_: dict | None = None


class ModelResponse(ModelBase):
    """Pydantic schema for returning AI model data via API"""

    id: int
    metadata_: dict | None = None
    created_at: datetime
    updated_at: datetime | None = None


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
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class BenchmarkCreate(BenchmarkBase):
    """Schema for creating a new benchmark via API"""

    pass


class BenchmarkUpdate(SQLModel):
    """Schema for updating a benchmark via API (all fields optional)"""

    name: str | None = Field(default=None, max_length=255)
    category: str | None = Field(default=None, max_length=100)
    description: str | None = None
    url: str | None = Field(default=None, max_length=500)


class BenchmarkResponse(BenchmarkBase):
    """Schema for benchmark in API responses"""

    id: int
    created_at: datetime
    updated_at: datetime | None = None


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
    model: Model = Relationship(back_populates="benchmark_results")
    benchmark: Benchmark = Relationship(back_populates="results")

    # Constraints
    __table_args__ = (
        # Prevent duplicate results for the same model+benchmark on the same date
        UniqueConstraint(
            "model_id", "benchmark_id", "date_tested", name="uix_model_benchmark_date"
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
    source: str | None = Field(default=None, max_length=255)


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
        default=None, sa_column=Column(ARRAY(String), nullable=True)
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
    sentiment: str | None = Field(default=None, max_length=50)
    source: str | None = Field(default=None, max_length=255)
    author: str | None = Field(default=None, max_length=255)
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

    use_case: str | None = Field(default=None, max_length=255)
    description: str | None = None
    mentioned_by: str | None = Field(default=None, max_length=255)


class UseCaseResponse(UseCaseBase):
    """Schema for use case in API responses"""

    id: int
    model_id: int
    created_at: datetime
    updated_at: datetime
