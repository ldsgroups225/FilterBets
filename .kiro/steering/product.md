# FilterBets Product Overview

## What is FilterBets?

FilterBets is a football betting analytics platform that helps users identify value betting opportunities through data-driven analysis, customizable filter strategies, and AI-powered predictions.

## Target Users

- **Sports Bettors** - Looking for data-driven betting decisions
- **Analytics Enthusiasts** - Interested in football statistics and trends
- **Strategy Builders** - Want to create and backtest custom betting strategies

## Core Features

### Pre-Match Scanner

Automated match analysis with customizable filter strategies. Users define criteria (odds ranges, team form, league selection) and the system identifies matches meeting those conditions.

### Backtesting Engine

Test betting strategies against historical data to evaluate performance before risking real money. Provides metrics like win rate, ROI, streaks, and drawdown analysis.

### Telegram Notifications

Real-time alerts when matches meet user-defined filter criteria. Integrates with Telegram for instant mobile notifications.

### Value Bet Detection

AI-powered identification of betting opportunities where bookmaker odds may be mispriced based on statistical analysis.

## Business Goals

1. Help users make informed betting decisions through data analysis
2. Provide transparent strategy performance metrics via backtesting
3. Reduce time spent manually analyzing matches
4. Enable strategy sharing and community learning

## Key Domain Concepts

### Filter Criteria Categories

- **Match Context:** League, date range, team selection
- **Odds-Based:** Home/Draw/Away win odds, Over/Under, BTTS
- **Probability:** AI-calculated win/draw/goal probabilities
- **Team Form:** Last N games stats, league position, points
- **Home/Away Splits:** Specific home/away performance metrics
- **Head-to-Head:** Historical matchup data

### Core Entities

- `leagues` - Football leagues (Premier League, La Liga, etc.)
- `teams` - Teams with stats and league associations
- `fixtures` - Match data with scores and status
- `odds` - Bookmaker odds for each fixture
- `team_stats` - Aggregated team statistics per season
- `users` - User accounts with Telegram integration
- `filters` - User-defined filter strategies (rules as JSONB)
- `filter_matches` - Matches that triggered a filter
- `backtest_results` - Historical backtest performance data
