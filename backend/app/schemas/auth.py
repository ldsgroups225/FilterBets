"""Authentication schemas for login, registration, and tokens."""

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    """Schema for user registration."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password (min 8 characters)")


class UserLogin(BaseModel):
    """Schema for user login."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class Token(BaseModel):
    """Schema for JWT token response."""

    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")


class UserInToken(BaseModel):
    """Schema for user info in auth response."""

    id: int
    email: str
    createdAt: str = Field(..., alias="created_at")
    updatedAt: str = Field(..., alias="updated_at")

    model_config = {"from_attributes": True, "populate_by_name": True}


class AuthResponse(BaseModel):
    """Schema for authentication response with tokens and user."""

    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    user: UserInToken = Field(..., description="Authenticated user info")


class TokenData(BaseModel):
    """Schema for decoded token data."""

    email: str | None = Field(None, description="User email from token")
    user_id: int | None = Field(None, description="User ID from token")


class RefreshTokenRequest(BaseModel):
    """Schema for refresh token request."""

    refresh_token: str = Field(..., description="JWT refresh token")
