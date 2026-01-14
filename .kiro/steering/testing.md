---
inclusion: manual
---

# Testing Standards

Use this guide when writing tests for FilterBets.

## Backend Testing (Pytest)

### Test File Structure

```text
backend/tests/
├── conftest.py           # Shared fixtures
├── test_auth.py          # Auth endpoint tests
├── test_filters.py       # Filter CRUD tests
├── test_backtest.py      # Backtest service tests
├── test_filter_engine.py # Filter engine unit tests
└── test_health.py        # Health check tests
```

### Test Class Organization

```python
import pytest
from httpx import AsyncClient

class TestFilterCRUD:
    """Tests for filter CRUD operations."""

    async def test_create_filter_success(self, client, auth_headers):
        """Test successful filter creation."""
        response = await client.post(
            "/api/v1/filters",
            json={"name": "Test Filter", "rules": [...]},
            headers=auth_headers,
        )
        assert response.status_code == 201
        assert response.json()["name"] == "Test Filter"

    async def test_create_filter_unauthorized(self, client):
        """Test filter creation without auth fails."""
        response = await client.post(
            "/api/v1/filters",
            json={"name": "Test", "rules": []},
        )
        assert response.status_code == 401
```

### Available Fixtures

From `conftest.py`:

```python
@pytest.fixture
async def db_session():
    """Async database session with transaction rollback."""
    # Automatically rolls back after each test

@pytest.fixture
async def client(db_session):
    """Async HTTP test client."""
    # Pre-configured with test database

@pytest.fixture
async def test_user(db_session):
    """Pre-created test user."""
    # email: test@example.com, password: testpassword

@pytest.fixture
async def auth_headers(test_user):
    """JWT auth headers for authenticated requests."""
    # Returns: {"Authorization": "Bearer <token>"}
```

### Testing Patterns

#### Testing API Endpoints

```python
async def test_get_filters_with_pagination(self, client, auth_headers, db_session):
    # Setup: Create test data
    for i in range(25):
        filter_obj = Filter(user_id=1, name=f"Filter {i}", rules=[])
        db_session.add(filter_obj)
    await db_session.commit()

    # Execute
    response = await client.get(
        "/api/v1/filters?page=2&per_page=10",
        headers=auth_headers,
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 10
    assert data["meta"]["page"] == 2
    assert data["meta"]["total"] == 25
```

#### Testing Services

```python
async def test_backtest_calculates_roi(self, db_session, setup_fixtures):
    # Setup
    service = BacktestService(db_session)
    filter_obj = Filter(rules=[{"field": "home_win_odds", "operator": ">=", "value": 2.0}])
    request = BacktestRequest(bet_type="home_win", seasons=[2024], stake=10.0)

    # Execute
    result = await service.run_backtest(filter_obj, request)

    # Assert
    assert result.total_matches > 0
    assert -100 <= result.roi_percentage <= 1000  # Reasonable ROI range
```

#### Testing Error Cases

```python
async def test_get_filter_not_found(self, client, auth_headers):
    response = await client.get("/api/v1/filters/99999", headers=auth_headers)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

async def test_create_filter_invalid_rules(self, client, auth_headers):
    response = await client.post(
        "/api/v1/filters",
        json={"name": "Test", "rules": [{"field": "invalid_field", "operator": "=", "value": 1}]},
        headers=auth_headers,
    )
    assert response.status_code == 422
```

### Running Tests

```bash
# Run all tests
cd backend && poetry run pytest tests/ -v

# Run specific test file
poetry run pytest tests/test_filters.py -v

# Run specific test class
poetry run pytest tests/test_filters.py::TestFilterCRUD -v

# Run with coverage
poetry run pytest tests/ -v --cov=app --cov-report=term-missing

# Run with short traceback
poetry run pytest tests/ -v --tb=short
```

## Frontend Testing (Vitest)

### Test Structure

```typescript
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { FilterCard } from './FilterCard';

describe('FilterCard', () => {
  const mockFilter = {
    id: 1,
    name: 'Test Filter',
    rules: [],
    isActive: true,
  };

  it('renders filter name', () => {
    render(<FilterCard filter={mockFilter} onEdit={vi.fn()} onDelete={vi.fn()} />);
    expect(screen.getByText('Test Filter')).toBeInTheDocument();
  });

  it('calls onEdit when edit button clicked', () => {
    const onEdit = vi.fn();
    render(<FilterCard filter={mockFilter} onEdit={onEdit} onDelete={vi.fn()} />);
    
    fireEvent.click(screen.getByRole('button', { name: /edit/i }));
    
    expect(onEdit).toHaveBeenCalledWith(1);
  });
});
```

### Running Frontend Tests

```bash
cd frontend
pnpm test              # Run tests in watch mode
pnpm test --run        # Run tests once
pnpm test --coverage   # Run with coverage
```

## Test Coverage Goals

- **Backend:** Minimum 75% coverage
- **Frontend:** Minimum 70% coverage
- **Critical paths:** 100% coverage (auth, payments, data mutations)

## Test Naming Convention

Use descriptive names that explain the scenario:

- `test_create_filter_success`
- `test_create_filter_unauthorized`
- `test_create_filter_invalid_rules`
- `test_backtest_with_no_matching_fixtures`
