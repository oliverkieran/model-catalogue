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


async def test_can_create_model(test_session, sample_models):
    """Test that we can insert and query a model using SQLModel"""
    sample_model = sample_models[0]
    test_session.add(sample_model)
    await test_session.commit()  # OK: commits the SAVEPOINT, not the outer transaction
    await test_session.refresh(sample_model)

    # Verify it has an ID and created_at timestamp
    assert sample_model.id is not None, "Model ID should not be None after insert"
    assert sample_model.created_at is not None, "Model should have created_at timestamp"

    # Prove it was actually written by querying the DB
    stmt = select(Model).where(Model.id == sample_model.id)
    row = (await test_session.exec(stmt)).first()

    assert row.name == sample_model.name
    assert row.display_name == sample_model.display_name
    assert row.organization == sample_model.organization


async def test_foreign_key_constraints(test_session, sample_models):
    """Test that foreign key relationships work correctly"""

    # Add the sample model first
    sample_model = sample_models[0]
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


async def test_unique_constraint(test_session, sample_models):
    """Test that the unique constraint on model name is enforced"""
    from sqlalchemy.exc import IntegrityError

    # Add the sample model first
    sample_model = sample_models[0]
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


async def test_jsonb_column(test_session, sample_models):
    """Test that JSONB columns work correctly"""
    sample_model = sample_models[0]
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


async def test_cascade_delete(test_session, sample_models):
    """Test that cascade delete works for related opinions"""
    sample_model = sample_models[0]
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
