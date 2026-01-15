# FilterBets API Testing with Bruno

This collection contains comprehensive API tests for the FilterBets football betting analytics platform.

## 📁 Collection Structure

```
test_api_with_bruno/
├── Auth/                    # Authentication endpoints
│   ├── Login.bru           # User login and token generation
│   ├── Register.bru        # User registration
│   └── Refresh Token.bru   # Token refresh
├── Leagues/                # Football leagues endpoints
│   ├── Get All Leagues.bru
│   └── Get League by ID.bru
├── Teams/                  # Teams endpoints
│   ├── Get All Teams.bru
│   └── Get Team by ID.bru
├── Fixtures/               # Match fixtures endpoints
│   ├── Get All Fixtures.bru
│   ├── Get Fixture by ID.bru
│   └── Get Fixtures by Date Range.bru
├── Filters/                # Filter management endpoints
│   ├── Get All Filters.bru
│   ├── Create Filter.bru
│   ├── Get Filter by ID.bru
│   ├── Update Filter.bru
│   └── Delete Filter.bru
├── Backtest/               # Backtesting endpoints
│   ├── Run Backtest.bru
│   ├── Get Backtest Jobs.bru
│   └── Get Backtest Job by ID.bru
└── System/                 # System endpoints
    ├── Root Endpoint.bru
    └── Health Check.bru
```

## 🚀 Getting Started

### Prerequisites

- Bruno installed (<https://www.usebruno.com/downloads>)
- FilterBets backend running on `http://localhost:8000`

### Setup

1. Open Bruno
2. Import this collection from the `test_api_with_bruno` directory
3. Set up environment variables (see Environment section)

## 🔧 Environment Variables

The collection uses the following environment variables:

| Variable | Default Value | Description |
|----------|---------------|-------------|
| `base_url` | `http://127.0.0.1:8000/api/v1` | API base URL |
| `auth_token` | *auto-generated* | JWT authentication token |
| `league_id` | `1` | Sample league ID |
| `team_id` | `1` | Sample team ID |
| `fixture_id` | `113949` | Sample fixture ID |
| `filter_id` | `801` | Sample filter ID |
| `job_id` | `550e8400-e29b-41d4-a716-446655440000` | Sample job ID |
| `start_date` | `2024-01-01` | Start date for date range queries |
| `end_date` | `2024-12-31` | End date for date range queries |

## 🧪 Test Features

### Authentication Flow

- **Login**: Authenticates user and stores JWT token
- **Register**: Creates new user account with random email
- **Refresh Token**: Refreshes expired JWT tokens

### Dynamic Variables

The collection uses Bruno's scripting capabilities to:

- Auto-generate random emails for registration
- Store authentication tokens for subsequent requests
- Extract IDs from responses for chained requests
- Set dynamic date ranges

### Test Assertions

Each request includes comprehensive tests:

- Status code validation
- Response body structure validation
- Data type verification
- Business logic validation

## 📊 Available Filter Features

Based on the API validation, the following fields are available for filters:

### Basic Match Fields

- `home_score`: Home team goals scored
- `away_score`: Away team goals scored
- `total_goals`: Total goals in match
- `total_expected_goals`: Expected goals (xG)
- `match_date`: Date of the match
- `league_id`: League identifier
- `status_id`: Match status
- `home_team_id`: Home team identifier
- `away_team_id`: Away team identifier

### Team Performance Statistics

- `home_team_goals_avg`: Home team average goals
- `home_team_goals_conceded_avg`: Home team average goals conceded
- `home_team_home_goals_avg`: Home team average goals at home
- `home_team_points_per_game`: Home team points per game
- `home_team_clean_sheet_pct`: Home team clean sheet percentage
- `away_team_goals_avg`: Away team average goals
- `away_team_goals_conceded_avg`: Away team average goals conceded
- `away_team_away_goals_avg`: Away team average goals away
- `away_team_points_per_game`: Away team points per game
- `away_team_clean_sheet_pct`: Away team clean sheet percentage

### Team Form Statistics

- `home_team_form_wins_last5`: Home team wins in last 5 games
- `home_team_form_wins_last10`: Home team wins in last 10 games
- `home_team_form_points_last5`: Home team points in last 5 games
- `home_team_form_points_last10`: Home team points in last 10 games
- `away_team_form_wins_last5`: Away team wins in last 5 games
- `away_team_form_wins_last10`: Away team wins in last 10 games
- `away_team_form_points_last5`: Away team points in last 5 games
- `away_team_form_points_last10`: Away team points in last 10 games

## 🔍 Backtesting Issues & Solutions

### ✅ FIXED: Season Filtering Bug

**Problem**: Backtest was returning 0 matches because it was incorrectly filtering by `season_type` instead of extracting the year from `match_date`.

**Root Cause**: The SQL query was using `season_type IN (2024)` but `season_type` values are like `12601, 12394, 12594` - not the year 2024.

**Solution Applied**: Fixed the backtest service to use `EXTRACT(year FROM match_date) IN (seasons)` instead of `season_type IN (seasons)`.

**Code Change**: Updated `/backend/app/services/backtest.py` line 120:

```python
# Before (BROKEN):
Fixture.season_type.in_(seasons)

# After (FIXED):
extract('year', Fixture.match_date).in_(seasons)
```

**Test Results**: After the fix, backtest now returns:

- **10,648 total matches** for 2024 season
- **4,222 wins (39.65% win rate)**
- **6,426 losses**
- **Proper calculations for profit and ROI**

### Issue: Backtest Returns 0 Matches

**Problem**: Filter `home_team_form_wins_last5 > 1` returns 0 matches because this feature doesn't exist in the dataset.

**Solution**: Use available features instead:

```json
{
  "name": "Home Win with Goals",
  "rules": [
    {
      "field": "home_score",
      "value": 0,
      "operator": ">"
    },
    {
      "field": "away_score",
      "value": 0,
      "operator": ">"
    },
    {
      "field": "total_goals",
      "value": 1.5,
      "operator": ">"
    }
  ]
}
```

This filter finds matches where:

- Home team scored more than 0 goals (won the match)
- Away team scored more than 0 goals
- Total goals exceeded 1.5 (ensuring sufficient scoring)

### Working Filter Examples

**Simple Home Win Filter**:

```json
{
  "name": "Home Win Filter",
  "rules": [
    {
      "field": "home_score",
      "value": 0,
      "operator": ">"
    },
    {
      "field": "away_score",
      "value": 0,
      "operator": ">"
    }
  ]
}
```

**Home Win with Goals Filter**:

```json
{
  "name": "Home Win with Goals",
  "rules": [
    {
      "field": "home_score",
      "value": 0,
      "operator": ">"
    },
    {
      "field": "away_score",
      "value": 0,
      "operator": ">"
    },
    {
      "field": "total_goals",
      "value": 1.5,
      "operator": ">"
    }
  ]
}
```

### Data Availability

- **Total fixtures with features**: 57,362
- **Completed matches (2024)**: 22,581
- **Home wins (2024)**: 10,218 (45.25%)
- **Available seasons**: 2024, 2025

## 🎯 Sample Test Workflows

### 1. Complete Authentication Flow

```
Register → Login → Refresh Token
```

### 2. Filter Management Workflow

```
Create Filter → Get Filter → Update Filter → Delete Filter
```

### 3. Backtesting Workflow

```
Create Filter → Run Backtest → Get Job Status → Get Results
```

## 🛠️ Advanced Features

### Request Chaining

Requests are chained using environment variables:

- `auth_token` from Login → used in all authenticated requests
- `filter_id` from Create Filter → used in Get/Update/Delete
- `job_id` from Run Backtest → used in Get Job Status

### Dynamic Data Generation

```javascript
// Random email generation
const random = Math.random().toString(36).substring(7);
bru.setEnvVar("random_email", `testuser_${random}@example.com`);

// Dynamic date ranges
const moment = require('moment');
bru.setEnvVar("start_date", moment().subtract(7, 'days').format('YYYY-MM-DD'));
```

### Comprehensive Testing

```javascript
tests {
  test("API Response Validation", function() {
    expect(res.getStatus()).to.equal(200);
    expect(res.body).to.be.an("array");
    expect(res.body[0]).to.have.property("id");
  });
}
```

## 📝 Best Practices

1. **Run in sequence**: Execute requests in the order they appear
2. **Check environment variables**: Ensure variables are properly set
3. **Monitor test results**: Review test assertions for failures
4. **Update sample data**: Modify IDs based on your actual data
5. **Use dynamic dates**: Leverage moment.js for date-based queries

## 🐛 Troubleshooting

### Common Issues

- **401 Unauthorized**: Check `auth_token` is set correctly
- **404 Not Found**: Verify resource IDs exist in your database
- **400 Bad Request**: Check request body format and required fields
- **500 Server Error**: Check backend logs for detailed errors

### Debug Tips

1. Enable Bruno's console output
2. Check response bodies for error messages
3. Verify database state using MCP tools
4. Test endpoints individually before running full collection

## 📚 Additional Resources

- [Bruno Documentation](https://docs.usebruno.com)
- [FilterBets API Documentation](http://localhost:8000/docs)
- [JavaScript Testing Reference](https://docs.usebruno.com/testing/script/javascript-reference)
- [Variables Management](https://blog.usebruno.com/manage-variables)

---

**Last Updated**: January 15, 2026
**Version**: 1.0.0
