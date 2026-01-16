# FastAPI-MCP Integration Guide

## Overview

FilterBets uses FastAPI-MCP to expose API endpoints as Model Context Protocol (MCP) tools for LLM integration. This enables AI assistants to test and interact with the API safely and intuitively.

## Configuration

The MCP server is configured in `backend/app/main.py` with the following best practices:

### Transport Method

- **HTTP Transport** (recommended): Uses the latest MCP Streamable HTTP specification
- Mounted at `/mcp` endpoint
- Provides better session management and connection handling

### Authentication

The MCP server requires JWT authentication for all requests:

```python
auth_config=AuthConfig(
    dependencies=[Depends(authenticate_mcp_request)],
)
```

**Authentication Requirements:**
- Include `Authorization: Bearer <token>` header in MCP requests
- Tokens must be valid JWT access tokens from `/api/v1/auth/login`
- Unauthorized requests receive 401 response

**Example MCP Client Configuration:**

```json
{
  "mcpServers": {
    "filterbets": {
      "url": "http://localhost:8000/mcp",
      "headers": {
        "Authorization": "Bearer your-jwt-token-here"
      }
    }
  }
}
```

### Server Metadata

```python
name="FilterBets API"
description="Football betting analytics API with filters, backtesting, and match data..."
```

### Schema Documentation

- `describe_full_response_schema=True` - Includes complete JSON schema in tool descriptions
- `describe_all_responses=True` - Documents all possible response types (success, errors, etc.)

### Safety Filtering

Excludes dangerous operations to prevent unintended data modification:

**Excluded Tags:**

- `auth` - User authentication endpoints
- `telegram` - Telegram integration endpoints

**Excluded Operations:**

- `delete_filter` - Prevents accidental filter deletion
- `update_filter` - Prevents unintended filter modifications
- `toggle_filter_alerts` - Prevents alert configuration changes

## Available MCP Tools

The MCP server exposes ~25 read-only tools organized by domain:

### Filters (6 tools)

- `list_filters` - Get user's filter strategies
- `get_filter` - Retrieve specific filter
- `create_filter` - Create new filter
- `get_filter_matches` - Find fixtures matching filter
- `run_filter_backtest` - Test filter against historical data

### Fixtures (4 tools)

- `list_fixtures` - Browse all fixtures with filters
- `get_today_fixtures` - Get today's matches
- `get_upcoming_fixtures` - Get upcoming matches
- `get_fixture_detail` - Get detailed fixture information

### Leagues (3 tools)

- `list_leagues` - Browse all leagues
- `get_league` - Get league details
- `get_league_teams` - Get teams in a league

### Teams (5 tools)

- `get_team` - Get team information
- `get_team_form` - Get team form/recent performance
- `get_team_match_stats` - Get stats for specific match
- `get_team_computed_stats` - Get pre-computed season stats
- `get_head_to_head` - Get head-to-head history

### Backtest (3 tools)

- `list_backtest_jobs` - Get backtest job history
- `get_backtest_job_status` - Check job status
- `cancel_backtest_job` - Cancel pending/running job

### Scanner (2 tools)

- `get_scanner_status` - Get scanner status
- `trigger_scanner` - Manually trigger scanner (admin only)

## Operation IDs

All endpoints have explicit `operation_id` parameters for clear, intuitive tool names:

```python
@router.get("/{filter_id}", operation_id="get_filter")
async def get_filter(...):
    """Get a specific filter by ID."""
```

Benefits:

- Clear, descriptive tool names for LLMs
- Consistent naming across all endpoints
- Easier to discover and use tools

## Testing the MCP Server

### Authentication

All MCP requests require JWT authentication:

```bash
# Get a token first
TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"your-password"}' | jq -r '.access_token')

# Use token in MCP requests
curl -H "Authorization: Bearer $TOKEN" \
  -H "Accept: text/event-stream" \
  http://localhost:8000/mcp
```

### Check MCP Endpoint

```bash
curl -H "Accept: text/event-stream" http://localhost:8000/mcp
```

Without authentication, requests will receive 401 Unauthorized.

### View Available Tools

The MCP tools are automatically generated from FastAPI endpoints. To see all available tools, connect an MCP client to `http://localhost:8000/mcp`.

### Example MCP Client Configuration

```json
{
  "mcpServers": {
    "filterbets": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

## Best Practices

### For LLM Integration

1. Use the MCP server for testing endpoints after implementing features
2. Rely on the read-only tools for data retrieval and analysis
3. Use the API directly for write operations (outside MCP)
4. Always include JWT token in MCP client configuration

### For Development

1. Add `operation_id` to all new endpoints for clarity
2. Keep endpoint descriptions concise and actionable
3. Use consistent naming conventions (snake_case for operation_ids)
4. Document response schemas thoroughly

### For Safety

1. Never expose destructive operations (DELETE, PUT) via MCP
2. Exclude sensitive endpoints (auth, admin operations)
3. Use `describe_all_responses=True` to document error cases
4. Test MCP tools before deploying to production
5. Require authentication for all MCP access

## References

- [FastAPI-MCP Documentation](../fastapi_mcp/docs/)
- [MCP Specification](https://modelcontextprotocol.io/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
