"""
Pytest configuration and shared fixtures
"""

import pytest
from datetime import date
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport
from sqlalchemy import event
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession

from app.config import settings
from app.main import app
from app.db.session import get_db
from app.models.models import Model, Benchmark


@pytest.fixture
def client():
    """FastAPI test client for unit testing endpoints."""
    return TestClient(app)


@pytest.fixture
async def client_with_db(test_session):
    """
    Async HTTP test client with overridden database dependency for integration tests.

    This fixture overrides the get_db dependency to use the test_session,
    ensuring that the API endpoints use the same database session as the test.
    This allows integration tests to see data created in the test session.
    """

    async def override_get_db():
        yield test_session

    app.dependency_overrides[get_db] = override_get_db

    # Use AsyncClient for async tests to share the same event loop
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client

    # Clean up dependency overrides after test
    app.dependency_overrides.clear()


@pytest.fixture
def sample_models():
    """
    List of three Sample AI models for testing
    """

    model1 = Model(
        name="gpt-model-1",
        display_name="GPT Model 1",
        organization="OpenAI-Test",
        release_date=date(2025, 1, 1),
        description="Test Model Nr. 1",
        license="Apache 2.0",
        metadata={"context_window": 64000, "pricing": "free"},
    )
    model2 = Model(
        name="claude-model-2",
        display_name="Model 2",
        organization="Anthropic-Test",
        release_date=date(2024, 6, 1),
        description="Test Model Nr. 2",
        license="Proprietary",
        metadata={"input_modalities": ["text", "images"], "pricing": "free"},
    )
    model3 = Model(
        name="gpt-model-3",
        display_name="GPT Model 3",
        organization="OpenAI-Test",
        release_date=date(2025, 6, 1),
        description="Test Model Nr. 3",
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
