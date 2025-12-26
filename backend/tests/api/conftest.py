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
