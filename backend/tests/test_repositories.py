"""
Tests for Repository Pattern Implementation

Tests all repository classes to ensure CRUD operations work correctly.
"""

from datetime import date

from app.db.repositories import (
    ModelRepository,
    BenchmarkRepository,
    BenchmarkResultRepository,
    OpinionRepository,
    UseCaseRepository,
)
from app.models.models import Model, Benchmark, BenchmarkResult, Opinion, UseCase

# =============================================================================
# ModelRepository Tests
# =============================================================================


async def test_model_repo_create(test_session, sample_models):
    """Test creating a model through the repository"""
    repo = ModelRepository(test_session)
    sample_model = sample_models[0]
    created = await repo.create(sample_model)

    assert created.id is not None
    assert created.name == sample_model.name
    assert created.organization == sample_model.organization
    assert created.created_at is not None


async def test_model_repo_get_by_id(test_session, sample_models):
    """Test retrieving a model by ID"""
    repo = ModelRepository(test_session)
    sample_model = sample_models[0]
    created = await repo.create(sample_model)
    retrieved = await repo.get_by_id(created.id)

    assert retrieved is not None
    assert retrieved.id == created.id
    assert retrieved.name == created.name


async def test_model_repo_get_by_id_not_found(test_session):
    "Test that get_by_id return None for non-existent ID"
    repo = ModelRepository(test_session)
    result = await repo.get_by_id(99999)
    assert result is None


async def test_mode_repo_get_by_name(test_session, sample_models):
    """Test retrieving a model by name"""
    repo = ModelRepository(test_session)
    sample_model = sample_models[0]
    created = await repo.create(sample_model)
    retrieved = await repo.get_by_name(created.name)

    assert retrieved is not None
    assert retrieved.name == sample_model.name
    assert retrieved.organization == sample_model.organization


async def test_model_repo_get_all(test_session):
    """Test retrieving all models with pagination"""
    repo = ModelRepository(test_session)

    # Create multiple AI models
    for i in range(5):
        model = Model(
            name=f"model-{i}",
            display_name=f"Model {i}",
            organization="Test Org",
        )
        await repo.create(model)

    # Get first 3
    first_three_records = await repo.get_all(limit=3)
    assert len(first_three_records) == 3

    # Get next 2
    next_two_records = await repo.get_all(skip=3, limit=2)
    assert len(next_two_records) == 2
    assert next_two_records[0].id not in [m.id for m in first_three_records]
    assert next_two_records[1].id not in [m.id for m in first_three_records]


async def test_model_repo_update(test_session, sample_models):
    """Test updating a model"""
    repo = ModelRepository(test_session)

    sample_model = sample_models[0]
    created = await repo.create(sample_model)
    original_id = created.id

    # Modify
    created.display_name = "Updated Display Name"
    created.organization = "Updated Org"

    # Update
    updated = await repo.update(created)

    assert updated.id == original_id
    assert updated.display_name == "Updated Display Name"
    assert updated.organization == "Updated Org"


async def test_model_repo_delete(test_session, sample_models):
    """Test deleting a model"""
    repo = ModelRepository(test_session)

    sample_model = sample_models[0]
    created = await repo.create(sample_model)
    model_id = created.id

    # Delete
    deleted = await repo.delete(model_id)
    assert deleted

    # Verify it's gone
    retrieved = await repo.get_by_id(model_id)
    assert retrieved is None


async def test_model_repo_delete_not_found(test_session):
    """Test deleting a non-existent model returns False"""
    repo = ModelRepository(test_session)

    result = await repo.delete(99999)
    assert result is False


async def test_model_repo_exists(test_session, sample_models):
    """Test checking if a model exists"""
    repo = ModelRepository(test_session)

    sample_model = sample_models[0]
    created = await repo.create(sample_model)

    assert await repo.exists(created.id) is True
    assert await repo.exists(99999) is False


async def test_model_repo_count(test_session):
    """Test counting total models"""
    repo = ModelRepository(test_session)

    initial_count = await repo.count()

    # Add 3 models
    for i in range(3):
        model = Model(
            name=f"count-model-{i}",
            display_name=f"Count Model {i}",
            organization="Count Org",
        )
        await repo.create(model)

    # Count should increase by 3
    new_count = await repo.count()
    assert new_count == initial_count + 3


async def test_model_repo_search(test_session, sample_models):
    """Test searching models by name or oranization"""
    repo = ModelRepository(test_session)

    for model in sample_models:
        await repo.create(model)

    results = await repo.search("gpt-model")
    assert len(results) == 2

    results = await repo.search("OpenAI-Test")
    assert len(results) == 2

    # Case insensitive search
    results = await repo.search("Anthropic-Test")
    assert len(results) == 1


async def test_model_repo_get_by_organization(test_session, sample_models):
    """Test getting models filtered by organization"""
    repo = ModelRepository(test_session)

    for model in sample_models:
        await repo.create(model)

    results = await repo.get_by_organization("OpenAI-Test")
    assert len(results) == 2
    assert results[0].name == "gpt-model-3"  # Newest first


async def test_model_repository_name_exists(test_session, sample_models):
    """Test checking if a model name already exists"""
    repo = ModelRepository(test_session)

    await repo.create(sample_models[0])

    # Name exists
    assert await repo.name_exists("gpt-model-1") is True

    # Name doesn't exist
    assert await repo.name_exists("non-existent-model") is False


async def test_model_repository_name_exists_exclude_id(test_session):
    """Test name_exists with exclude_id for updates"""
    repo = ModelRepository(test_session)

    model = Model(
        name="original-name", display_name="Original", organization="Test Org"
    )
    created = await repo.create(model)

    # Same name, excluding own ID -> should return False (name is available for this model)
    assert await repo.name_exists("original-name", exclude_id=created.id) is False

    # Create another model
    other_model = Model(
        name="other-name", display_name="Other", organization="Test Org"
    )
    await repo.create(other_model)

    # Try to take other model's name -> should return True (conflict)
    assert await repo.name_exists("other-name", exclude_id=created.id) is True


# =============================================================================
# BenchmarkRepository Tests
# =============================================================================


async def test_benchmark_repo_create(test_session, sample_benchmark):
    """Test creating a benchmark through the repository"""
    repo = BenchmarkRepository(test_session)

    created = await repo.create(sample_benchmark)

    assert created.id is not None
    assert created.name == sample_benchmark.name
    assert created.description == sample_benchmark.description
    assert created.created_at is not None


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
        Benchmark(name="MATH", category="Math-Test", description="Math problems"),
        Benchmark(name="GSM8K", category="Math-Test", description="Grade school math"),
    ]

    for bench in benchmarks:
        await repo.create(bench)

    # Get math benchmarks
    results = await repo.get_by_category("Math-Test")
    assert len(results) == 2
    assert all(b.category == "Math-Test" for b in results)


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
    assert len(set(categories)) >= 3
    assert "Knowledge" in categories
    assert "Coding" in categories
    assert "Math" in categories


# =============================================================================
# BenchmarkResultRepository Tests
# =============================================================================


async def test_benchmark_result_repository_create(
    test_session, sample_models, sample_benchmark
):
    """Test creating a benchmark result"""
    model_repo = ModelRepository(test_session)
    benchmark_repo = BenchmarkRepository(test_session)
    bm_result_repo = BenchmarkResultRepository(test_session)

    # Create model and benchmark first
    model = await model_repo.create(sample_models[0])
    benchmark = await benchmark_repo.create(sample_benchmark)

    # Create result
    result = BenchmarkResult(
        model_id=model.id,
        benchmark_id=benchmark.id,
        score=85.5,
        date_tested=date(2025, 1, 15),
        source="Test Suite",
    )

    created = await bm_result_repo.create(result)

    assert created.id is not None
    assert created.score == 85.5
    assert created.model_id == model.id
    assert created.benchmark_id == benchmark.id


async def test_benchmark_result_repository_get_by_model_id(test_session):
    """Test getting all results for a model"""
    model_repo = ModelRepository(test_session)
    benchmark_repo = BenchmarkRepository(test_session)
    bm_result_repo = BenchmarkResultRepository(test_session)

    model1 = await model_repo.create(
        Model(name="model-1", display_name="Model1", organization="Test")
    )
    model2 = await model_repo.create(
        Model(name="model-2", display_name="Model2", organization="Test")
    )

    # Create multiple benchmarks
    bench1 = await benchmark_repo.create(
        Benchmark(name="BENCH1", category="Testing", description="First test benchmark")
    )
    bench2 = await benchmark_repo.create(
        Benchmark(
            name="BENCH2", category="Testing", description="Second test benchmark"
        )
    )

    # Create results for same model
    await bm_result_repo.create(
        BenchmarkResult(model_id=model1.id, benchmark_id=bench1.id, score=80.0)
    )
    await bm_result_repo.create(
        BenchmarkResult(model_id=model1.id, benchmark_id=bench2.id, score=90.0)
    )
    await bm_result_repo.create(
        BenchmarkResult(model_id=model2.id, benchmark_id=bench1.id, score=70.0)
    )  # Different model

    # Get all results for this model
    results = await bm_result_repo.get_by_model_id(model1.id)

    assert len(results) == 2
    assert all(r.model_id == model1.id for r in results)


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
    test_session, sample_models, sample_benchmark
):
    """Test getting results for specific model-benchmark pair"""
    model_repo = ModelRepository(test_session)
    benchmark_repo = BenchmarkRepository(test_session)
    result_repo = BenchmarkResultRepository(test_session)

    model = await model_repo.create(sample_models[0])
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
    assert all(
        r.model_id == model.id and r.benchmark_id == benchmark.id for r in results
    )


async def test_benchmark_result_repository_result_exists(
    test_session, sample_models, sample_benchmark
):
    """Test checking if a result already exists"""
    model_repo = ModelRepository(test_session)
    benchmark_repo = BenchmarkRepository(test_session)
    result_repo = BenchmarkResultRepository(test_session)

    model = await model_repo.create(sample_models[0])
    benchmark = await benchmark_repo.create(sample_benchmark)

    test_date = date(2024, 1, 15)

    # Initially doesn't exist
    assert (await result_repo.result_exists(model.id, benchmark.id, test_date)) is False

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
    assert (await result_repo.result_exists(model.id, benchmark.id, test_date)) is True

    # Different date doesn't exist
    assert (
        await result_repo.result_exists(model.id, benchmark.id, date(2024, 2, 1))
    ) is False


# =============================================================================
# OpinionRepository Tests
# =============================================================================


async def test_opinion_repository_get_by_model_id(test_session, sample_models):
    """Test getting opinions by model ID"""
    model_repo = ModelRepository(test_session)
    opinion_repo = OpinionRepository(test_session)

    for model in sample_models[:2]:
        await model_repo.create(model)

    # Create opinions for same model
    await opinion_repo.create(
        Opinion(model_id=sample_models[0].id, content="The model is great for coding.")
    )
    await opinion_repo.create(
        Opinion(model_id=sample_models[0].id, content="Amazing coding model")
    )
    await opinion_repo.create(
        Opinion(model_id=sample_models[1].id, content="Much worse than model 1")
    )  # Different model

    # Get all opinions for this model
    opinions = await opinion_repo.get_by_model_id(sample_models[0].id)
    assert len(opinions) == 2
    assert all(o.model_id == sample_models[0].id for o in opinions)


async def test_opinion_repository_get_by_sentiment(test_session, sample_models):
    """Test getting opinions by sentiment"""
    model_repo = ModelRepository(test_session)
    opinion_repo = OpinionRepository(test_session)

    model1 = sample_models[0]
    model2 = sample_models[1]
    await model_repo.create(model1)
    await model_repo.create(model2)

    # Create opinions for same model
    await opinion_repo.create(
        Opinion(
            model_id=model1.id,
            content="The model is great for coding.",
            sentiment="positive",
        )
    )
    await opinion_repo.create(
        Opinion(
            model_id=model1.id, content="Amazing coding model", sentiment="positive"
        )
    )
    await opinion_repo.create(
        Opinion(
            model_id=model2.id, content="Much worse than model 1", sentiment="negative"
        )
    )

    # Get all opinions for this model
    opinions = await opinion_repo.get_by_sentiment("positive")
    assert len(opinions) == 2
    assert all(o.sentiment == "positive" for o in opinions)


async def test_opinion_repository_search_by_content(test_session, sample_models):
    """Test searching opinions by content keyword"""
    model_repo = ModelRepository(test_session)
    opinion_repo = OpinionRepository(test_session)

    model1 = sample_models[0]
    await model_repo.create(model1)

    # Create opinions for the model
    await opinion_repo.create(
        Opinion(
            model_id=model1.id,
            content="The model is great for coding tasks.",
        )
    )
    await opinion_repo.create(
        Opinion(
            model_id=model1.id,
            content="Amazing performance in creative writing.",
        )
    )
    await opinion_repo.create(
        Opinion(
            model_id=model1.id,
            content="Not suitable for coding challenges.",
        )
    )

    # Search for opinions containing 'coding'
    opinions = await opinion_repo.search_by_content("coding")
    assert len(opinions) == 2
    assert all("coding" in o.content.lower() for o in opinions)


# =============================================================================
# UseCaseRepository Tests
# =============================================================================


async def test_usecase_repository_get_by_model_id(test_session, sample_models):
    """Test getting use cases by model ID"""
    model_repo = ModelRepository(test_session)
    usecase_repo = UseCaseRepository(test_session)

    for model in sample_models[:2]:
        await model_repo.create(model)

    # Create use cases for same model
    await usecase_repo.create(
        UseCase(
            model_id=sample_models[0].id, use_case="coding", description="Coding tasks"
        )
    )
    await usecase_repo.create(
        UseCase(
            model_id=sample_models[0].id,
            use_case="creative-writing",
            description="Creative writing tasks",
        )
    )
    await usecase_repo.create(
        UseCase(
            model_id=sample_models[1].id,
            use_case="data-analysis",
            description="Data analysis tasks",
        )
    )  # Different model

    # Get all use cases for this model
    use_cases = await usecase_repo.get_by_model_id(sample_models[0].id)
    assert len(use_cases) == 2
    assert all(uc.model_id == sample_models[0].id for uc in use_cases)


async def test_usecase_repository_get_by_use_case(test_session, sample_models):
    """Test getting use cases by use case name"""
    model_repo = ModelRepository(test_session)
    usecase_repo = UseCaseRepository(test_session)

    for model in sample_models[:2]:
        await model_repo.create(model)

    # Create use cases for different models
    await usecase_repo.create(
        UseCase(
            model_id=sample_models[0].id, use_case="RAG", description="Coding tasks"
        )
    )
    await usecase_repo.create(
        UseCase(
            model_id=sample_models[1].id,
            use_case="RAG",
            description="Advanced coding tasks",
        )
    )
    await usecase_repo.create(
        UseCase(
            model_id=sample_models[1].id,
            use_case="data-analysis",
            description="Data analysis tasks",
        )
    )

    # Get all use cases for 'RAG'
    use_cases = await usecase_repo.get_by_use_case("RAG")
    assert len(use_cases) == 2
    assert all(uc.use_case == "RAG" for uc in use_cases)
