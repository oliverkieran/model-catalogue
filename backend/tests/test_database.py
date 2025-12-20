"""
Database connection and schema tests with SQLModel and Async SQLAlchemy
"""

import pytest
from sqlalchemy import text, inspect
from app.models.models import Model


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


async def test_can_create_model(test_session):
    """Test that we can insert and query a model using SQLModel"""
    test_model = Model(
        name="gpt-test",
        display_name="GPT Test Model",
        organization="Test Org",
        description="A test model for unit testing.",
    )
    test_session.add(test_model)
    await test_session.commit()  # Write to DB without committing
    await test_session.refresh(test_model)

    # Verify it has an ID and created_at timestamp
    assert test_model.id is not None, "Model ID should not be None after insert"
    assert test_model.created_at is not None, "Model should have created_at timestamp"

    # Clean up - delete the test model
    await test_session.delete(test_model)
    await test_session.commit()
