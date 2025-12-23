"""
Pytest configuration and shared fixtures
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession
from app.main import app
from app.config import settings
from app.models.models import Model, Benchmark
from datetime import date


@pytest.fixture
def client():
    """
    Create a test client for the FastAPI application
    """
    return TestClient(app)


@pytest.fixture
def sample_models():
    """
    List of three Sample AI models for testing
    """

    model1 = Model(
        name=f"gpt-model-1",
        display_name=f"GPT Model 1",
        organization="OpenAI-Test",
        release_date=date(2025, 1, 1),
        description=f"Test Model Nr. 1",
        license="Apache 2.0",
        metadata={"context_window": 64000, "pricing": "free"},
    )
    model2 = Model(
        name=f"claude-model-2",
        display_name=f"Model 2",
        organization="Anthropic-Test",
        release_date=date(2024, 6, 1),
        description=f"Test Model Nr. 2",
        license="Proprietary",
        metadata={"input_modalities": ["text", "images"], "pricing": "free"},
    )
    model3 = Model(
        name=f"gpt-model-3",
        display_name=f"GPT Model 3",
        organization="OpenAI-Test",
        release_date=date(2025, 6, 1),
        description=f"Test Model Nr. 3",
        license="Proprietary",
        metadata={"context_window": 128000, "pricing": "expensive"},
    )

    return [model1, model2, model3]


@pytest.fixture
def sample_benchmark():
    """Sample benchmark for testing"""
    return Benchmark(
        name="TEST_BENCH",
        category="Reasoning",
        description="A benchmark for testing AI models",
        url="https://example.com/test-bench",
    )


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
