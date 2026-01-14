---
inclusion: manual
---

# API Design Standards

Use this guide when designing new API endpoints or modifying existing ones.

## RESTful Conventions

### HTTP Methods

| Method | Purpose | Example |
| -------- | --------- | --------- |
| GET | Retrieve resource(s) | `GET /filters` |
| POST | Create resource | `POST /filters` |
| PUT | Full update | `PUT /filters/{id}` |
| PATCH | Partial update | `PATCH /filters/{id}` |
| DELETE | Remove resource | `DELETE /filters/{id}` |

### URL Structure

```text
/api/v1/{resource}              # Collection
/api/v1/{resource}/{id}         # Single resource
/api/v1/{resource}/{id}/{sub}   # Sub-resource
```

### Naming Rules

- Use plural nouns: `/filters` not `/filter`
- Use kebab-case for multi-word: `/backtest-jobs`
- Avoid verbs in URLs (use HTTP methods instead)

## Request/Response Patterns

### Successful Responses

```json
// GET /filters - List
{
  "items": [...],
  "meta": {
    "page": 1,
    "per_page": 20,
    "total": 45,
    "total_pages": 3
  }
}

// GET /filters/{id} - Single
{
  "id": 1,
  "name": "High Odds Filter",
  "rules": [...],
  "created_at": "2024-01-15T10:30:00Z"
}

// POST /filters - Create (201 Created)
{
  "id": 2,
  "name": "New Filter",
  ...
}
```

### Error Responses

```json
// 400 Bad Request
{
  "detail": "Validation error",
  "errors": [
    {"field": "name", "message": "Name is required"},
    {"field": "rules", "message": "At least one rule is required"}
  ]
}

// 401 Unauthorized
{
  "detail": "Not authenticated"
}

// 403 Forbidden
{
  "detail": "Not authorized to access this resource"
}

// 404 Not Found
{
  "detail": "Filter not found"
}

// 422 Unprocessable Entity
{
  "detail": "Invalid filter rule: unknown field 'xyz'"
}
```

## Status Codes

| Code | Meaning | When to Use |
| ------ | --------- | ------------- |
| 200 | OK | Successful GET, PUT, PATCH |
| 201 | Created | Successful POST |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Invalid request format |
| 401 | Unauthorized | Missing/invalid auth |
| 403 | Forbidden | Valid auth, no permission |
| 404 | Not Found | Resource doesn't exist |
| 422 | Unprocessable | Valid format, invalid data |
| 500 | Server Error | Unexpected server error |

## Pagination

### Query Parameters

```text
GET /fixtures?page=2&per_page=50&sort=-match_date
```

- `page` - Page number (default: 1)
- `per_page` - Items per page (default: 20, max: 100)
- `sort` - Sort field (prefix `-` for descending)

### Response Format

```json
{
  "items": [...],
  "meta": {
    "page": 2,
    "per_page": 50,
    "total": 234,
    "total_pages": 5
  }
}
```

## Filtering

### Query Parameters

```text
GET /fixtures?league_id=1&status=completed&date_from=2024-01-01
```

### Filter Operators

For complex filtering, use bracket notation:

```text
GET /fixtures?home_win_odds[gte]=2.0&home_win_odds[lte]=3.5
```

## Authentication

### JWT Bearer Token

```text
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### Protected Endpoints

All endpoints except `/auth/login` and `/auth/register` require authentication.

## Versioning

API version is in the URL path: `/api/v1/...`

When making breaking changes:

1. Create new version `/api/v2/...`
2. Maintain old version for deprecation period
3. Document migration path

## Documentation

All endpoints must have:

- Summary (short description)
- Description (detailed explanation)
- Request body schema (if applicable)
- Response schema
- Error responses
- Example values

FastAPI auto-generates OpenAPI docs at `/docs`.
