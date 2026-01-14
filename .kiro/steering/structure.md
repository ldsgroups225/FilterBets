# FilterBets Project Structure

## Directory Layout

```text
FilterBets/
├── backend/                    # Python FastAPI backend
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/            # Versioned API endpoints
│   │   │       ├── auth.py
│   │   │       ├── backtest.py
│   │   │       ├── filters.py
│   │   │       ├── fixtures.py
│   │   │       ├── leagues.py
│   │   │       └── teams.py
│   │   ├── models/            # SQLAlchemy ORM models
│   │   ├── schemas/           # Pydantic request/response schemas
│   │   ├── services/          # Business logic layer
│   │   ├── tasks/             # Celery background tasks
│   │   ├── utils/             # Helper functions
│   │   ├── config.py          # Settings management
│   │   ├── database.py        # DB connection setup
│   │   └── main.py            # FastAPI app entry point
│   ├── tests/                 # Pytest test files
│   ├── alembic/               # Database migrations
│   ├── pyproject.toml         # Poetry dependencies
│   └── Dockerfile
├── frontend/                   # React TypeScript frontend
│   ├── src/
│   │   ├── components/        # Reusable UI components
│   │   ├── pages/             # Route pages
│   │   ├── hooks/             # Custom React hooks
│   │   ├── services/          # API client functions
│   │   ├── types/             # TypeScript type definitions
│   │   └── utils/             # Helper functions
│   ├── package.json
│   └── vite.config.ts
├── data/                       # Data files and scripts
│   ├── base_data/             # Core fixture data
│   ├── lineup_data/           # Team lineup data
│   ├── playerStats_data/      # Player statistics
│   └── download_data.py       # Data ingestion script
├── tasks/                      # PRDs and task lists
│   ├── prd-*.md               # Product requirement docs
│   └── tasks-*.md             # Implementation task lists
├── agent-template/             # AI workflow templates
│   ├── create-prd.md
│   └── generate-tasks.md
├── docker-compose.yml
├── docker-compose.prod.yml
└── AGENTS.md                   # AI development guide
```

## Naming Conventions

### Python (Backend)

- **Files:** `snake_case.py` (e.g., `filter_engine.py`)
- **Classes:** `PascalCase` (e.g., `BacktestService`)
- **Functions/Variables:** `snake_case` (e.g., `calculate_roi`)
- **Constants:** `UPPER_SNAKE_CASE` (e.g., `DEFAULT_STAKE`)

### TypeScript (Frontend)

- **Files:** `PascalCase.tsx` for components, `camelCase.ts` for utilities
- **Components:** `PascalCase` (e.g., `FilterBuilder`)
- **Functions/Variables:** `camelCase` (e.g., `fetchFixtures`)
- **Types/Interfaces:** `PascalCase` (e.g., `FilterRule`)

### Database

- **Tables:** `snake_case` plural (e.g., `team_stats`, `backtest_jobs`)
- **Columns:** `snake_case` (e.g., `created_at`, `home_team_id`)

## Import Patterns

### Backend Imports

```python
# Standard library first
from datetime import datetime
from typing import Any

# Third-party packages
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

# Local imports (absolute from app)
from app.api.deps import get_current_user, get_db
from app.models.filter import Filter
from app.schemas.filter import FilterCreate, FilterResponse
from app.services.filter_engine import FilterEngine
```

### Frontend Imports

```typescript
// React and third-party first
import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';

// UI components
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';

// Local components and utilities
import { FilterBuilder } from '@/components/FilterBuilder';
import { fetchFilters } from '@/services/api';
import type { Filter } from '@/types';
```

## API Endpoint Patterns

All API endpoints follow RESTful conventions under `/api/v1/`:

| Resource | Endpoint Pattern |
| ---------- | ----------------- |
| Auth | `/api/v1/auth/login`, `/api/v1/auth/register` |
| Filters | `/api/v1/filters`, `/api/v1/filters/{id}` |
| Fixtures | `/api/v1/fixtures`, `/api/v1/fixtures/today` |
| Leagues | `/api/v1/leagues`, `/api/v1/leagues/{id}` |
| Teams | `/api/v1/teams/{id}`, `/api/v1/teams/{id}/stats` |
| Backtest | `/api/v1/backtest/jobs`, `/api/v1/filters/{id}/backtest` |

## File Organization Rules

1. **One model per file** in `backend/app/models/`
2. **One router per domain** in `backend/app/api/v1/`
3. **Services encapsulate business logic** - keep routes thin
4. **Schemas mirror models** but separate request/response concerns
5. **Tests mirror source structure** - `test_filters.py` tests `filters.py`
