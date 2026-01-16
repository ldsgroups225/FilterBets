"""Authentication endpoints for user registration, login, and token management."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.auth import AuthResponse, RefreshTokenRequest, UserCreate, UserInToken, UserLogin
from app.schemas.user import UserResponse
from app.services.auth import (
    authenticate_user,
    create_tokens,
    create_user,
    get_user_by_email,
)
from app.utils.security import decode_token

router = APIRouter()


def create_auth_response(user: User) -> AuthResponse:
    """Create an AuthResponse with tokens and user info."""
    tokens = create_tokens(user)
    user_info = UserInToken(
        id=user.id,
        email=user.email,
        created_at=user.created_at.isoformat(),
        updated_at=user.updated_at.isoformat(),
    )
    return AuthResponse(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
        token_type=tokens.token_type,
        user=user_info,
    )


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    session: Annotated[AsyncSession, Depends(get_db)],
) -> AuthResponse:
    """Register a new user account and return tokens.

    Args:
        user_data: User registration data
        session: Database session

    Returns:
        Auth response with tokens and user info

    Raises:
        HTTPException: If email already registered
    """
    # Check if user already exists
    existing_user = await get_user_by_email(session, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create new user
    user = await create_user(session, user_data.email, user_data.password)
    return create_auth_response(user)


@router.post("/login", response_model=AuthResponse)
async def login(
    credentials: UserLogin,
    session: Annotated[AsyncSession, Depends(get_db)],
) -> AuthResponse:
    """Authenticate user and return JWT tokens.

    Args:
        credentials: User login credentials
        session: Database session

    Returns:
        Auth response with tokens and user info

    Raises:
        HTTPException: If credentials are invalid
    """
    user = await authenticate_user(session, credentials.email, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return create_auth_response(user)


@router.post("/refresh", response_model=AuthResponse)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    session: Annotated[AsyncSession, Depends(get_db)],
) -> AuthResponse:
    """Refresh access token using refresh token.

    Args:
        refresh_data: Refresh token request
        session: Database session

    Returns:
        New auth response with tokens and user info

    Raises:
        HTTPException: If refresh token is invalid
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_token(refresh_data.refresh_token)
        user_id: int | None = payload.get("user_id")
        token_type: str | None = payload.get("type")

        if user_id is None or token_type != "refresh":
            raise credentials_exception

    except JWTError:
        raise credentials_exception from None

    # Get user from database
    from app.services.auth import get_user_by_id

    user = await get_user_by_id(session, user_id=user_id)
    if user is None or not user.is_active:
        raise credentials_exception

    # Create new tokens
    return create_auth_response(user)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Get current authenticated user information.

    Args:
        current_user: Current authenticated user

    Returns:
        Current user object
    """
    return current_user
