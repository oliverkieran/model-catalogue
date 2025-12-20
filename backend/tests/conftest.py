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
from app.models.models import Model
from datetime import date


@pytest.fixture
def client():
    """
    Create a test client for the FastAPI application
    """
    return TestClient(app)


@pytest.fixture
def sample_model():
    """
    Sample model for testing
    """
    return Model(
        name="gpt-test",
        display_name="GPT Test Model",
        organization="Test Org",
        release_date=date(2025, 1, 1),
        description="Large Language Model for testing purposes",
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
