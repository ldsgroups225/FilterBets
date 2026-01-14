"""Tests for health and root endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_root_endpoint(client: AsyncClient) -> None:
    """Test the root endpoint returns API info."""
    response = await client.get("/")
    assert response.status_code == 200

    data = response.json()
    assert "name" in data
    assert "version" in data
    assert "docs" in data
    assert "health" in data
    assert data["name"] == "FilterBets API"
    assert data["docs"] == "/docs"


@pytest.mark.asyncio
async def test_health_endpoint(client: AsyncClient) -> None:
    """Test the health endpoint returns status."""
    response = await client.get("/health")
    assert response.status_code == 200

    data = response.json()
    assert "status" in data
    assert "database" in data
    assert data["status"] == "healthy"
    # Database will be disconnected in test environment without DB
    assert data["database"] in ["connected", "disconnected"]


@pytest.mark.asyncio
async def test_docs_endpoint(client: AsyncClient) -> None:
    """Test the OpenAPI docs endpoint is accessible."""
    response = await client.get("/docs")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_openapi_schema(client: AsyncClient) -> None:
    """Test the OpenAPI schema endpoint."""
    response = await client.get("/openapi.json")
    assert response.status_code == 200

    data = response.json()
    assert "openapi" in data
    assert "info" in data
    assert data["info"]["title"] == "FilterBets API"
