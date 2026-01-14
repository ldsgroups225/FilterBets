"""Authentication service for user authentication and token management."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.auth import Token
from app.utils.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
)


async def authenticate_user(session: AsyncSession, email: str, password: str) -> User | None:
    """Authenticate a user by email and password.

    Args:
        session: Database session
        email: User email
        password: Plain text password

    Returns:
        User object if authentication successful, None otherwise
    """
    result = await session.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user:
        return None

    if not verify_password(password, user.password_hash):
        return None

    if not user.is_active:
        return None

    return user


async def create_user(session: AsyncSession, email: str, password: str) -> User:
    """Create a new user account.

    Args:
        session: Database session
        email: User email
        password: Plain text password

    Returns:
        Created user object
    """
    hashed_password = get_password_hash(password)
    user = User(email=email, password_hash=hashed_password)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    """Get a user by email address.

    Args:
        session: Database session
        email: User email

    Returns:
        User object if found, None otherwise
    """
    result = await session.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_id(session: AsyncSession, user_id: int) -> User | None:
    """Get a user by ID.

    Args:
        session: Database session
        user_id: User ID

    Returns:
        User object if found, None otherwise
    """
    result = await session.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


def create_tokens(user: User) -> Token:
    """Create access and refresh tokens for a user.

    Args:
        user: User object

    Returns:
        Token object with access and refresh tokens
    """
    token_data = {"sub": user.email, "user_id": user.id}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return Token(access_token=access_token, refresh_token=refresh_token)
