"""Pytest configuration and fixtures for tests."""

import asyncio
from collections.abc import AsyncGenerator, Generator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.api.deps import get_db
from app.config import get_settings
from app.main import app

settings = get_settings()

# Test database URL (use the same database for now, but with isolated tables per test)
TEST_DATABASE_URL = settings.database_url

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    poolclass=NullPool,
    echo=False,
)

# Create test session maker
TestSessionLocal = sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)  # type: ignore


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function", autouse=True)
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a fresh database session for each test with transaction rollback."""
    # Create connection
    async with test_engine.connect() as connection:
        # Start a transaction
        transaction = await connection.begin()

        # Create session bound to this connection
        session = AsyncSession(bind=connection, expire_on_commit=False, join_transaction_mode="create_savepoint")

        try:
            yield session
        finally:
            # Always rollback the transaction after test
            await session.close()
            await transaction.rollback()


@pytest.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client with database session override."""

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
async def test_user(db_session: AsyncSession):
    """Create a test user for authentication tests."""
    from app.models.user import User
    from app.utils.security import get_password_hash

    user = User(
        email="test@example.com",
        password_hash=get_password_hash("testpassword123"),
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
async def auth_headers(client: AsyncClient, test_user) -> dict[str, str]:  # noqa: ARG001
    """Get authentication headers for a test user."""
    from app.utils.security import create_access_token

    access_token = create_access_token({"sub": test_user.email, "user_id": test_user.id})
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture(scope="function")
async def db(db_session: AsyncSession) -> AsyncSession:
    """Alias for db_session to match test expectations."""
    return db_session
