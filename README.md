# FilterBets

A football betting analytics platform with AI-powered predictions, backtesting, and Telegram notifications.

## Features

- **Pre-Match Scanner** - Automated match analysis with customizable filter strategies
- **Backtesting Engine** - Test strategies against historical data with advanced metrics
- **Telegram Notifications** - Real-time alerts when matches meet filter criteria
- **Value Bet Detection** - AI-powered identification of betting opportunities
- **MCP Integration** - API accessible via Model Context Protocol for AI assistants

## Current Status

### Latest Changes (v1.2.0)

**Phase 1: Data Quality**
- ✅ Added look-ahead bias prevention with `POST_MATCH_FIELDS` validation
- ✅ Added real odds support with `OddsStats` schema
- ✅ Created odds import script (`backend/scripts/import_odds.py`)

**Phase 2: Bug Fixes**
- ✅ Fixed Greenlet/Session errors with eager loading
- ✅ Fixed Celery worker and Telegram bot container health

**Phase 3: Features**
- ✅ Added JWT authentication to FastAPI-MCP
- ✅ Added advanced backtest metrics (Kelly Criterion, EV, Confidence Intervals, Statistical Significance)
- ✅ Added filter validation endpoint (`POST /api/v1/filters/validate`)
- ✅ New documentation: `docs/backtest-metrics.md`

**Phase 4: In Progress**
- 🔄 Premier League data import script
- 🔄 Integration tests
- 📋 Documentation updates

### Quick Stats

| Metric | Value |
|--------|-------|
| Fixtures in DB | 66,836 |
| Available in CSV | 83,185 |
| Premier League matches | 3,148 |
| Test Coverage | 44% |

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 18 / TypeScript / TanStack Query / Tailwind CSS / shadcn/ui |
| Backend | FastAPI / SQLAlchemy 2.0 / Alembic |
| Database | PostgreSQL 16 |
| Cache | Redis 7 |
| Task Queue | Celery + Celery Beat |
| DevOps | Docker / Docker Compose / GitHub Actions |

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.12+ with Poetry
- Node.js 20+ with pnpm
- Telegram Bot Token (for notifications)

### Environment Setup

1. **Create a Telegram Bot** (for notifications feature):
   - Open Telegram and search for [@BotFather](https://t.me/botfather)
   - Send `/newbot` and follow the instructions
   - Save the bot token provided
   - Send `/setcommands` to BotFather and set these commands:

     ```text
     start - Link your Telegram account
     status - Check your account status
     filters - List your active filters
     unlink - Unlink your Telegram account
     help - Show available commands
     ```

2. **Configure Environment Variables**:

   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your Telegram bot credentials:

   ```env
   # Telegram Bot Configuration
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   TELEGRAM_BOT_USERNAME=YourBotUsername
   TELEGRAM_LINK_TOKEN_TTL=1800  # 30 minutes
   
   # Scanner Configuration
   SCANNER_LOOKAHEAD_HOURS=24
   SCANNER_MAX_NOTIFICATIONS_PER_SCAN=1000
   ```

### Using Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/filterbets.git
cd filterbets

# Copy environment variables
cp .env.example .env

# Start all services
make up

# View logs
make logs
```

Services will be available at:

- Frontend: <http://localhost:5173>
- Backend API: <http://localhost:8000>
- API Docs: <http://localhost:8000/docs>

The following services will run automatically:

- **Backend API** - FastAPI application
- **Frontend** - React development server
- **PostgreSQL** - Database (port 5433)
- **Redis** - Cache and message broker
- **Celery Worker** - Background task processor
- **Celery Beat** - Task scheduler for periodic scans
- **Telegram Bot** - Notification bot (requires TELEGRAM_BOT_TOKEN)

### Telegram Bot Setup

The Telegram bot runs as a separate service and handles:

- Account linking via deep links
- Real-time match notifications
- Filter status queries

**To start the bot manually** (if not using Docker):

```bash
cd backend
poetry run python -m app.bot.run_bot
```

**Bot Commands**:

- `/start` - Link your Telegram account (use the link from Settings page)
- `/status` - View your linked account and active filters
- `/filters` - List all your active filters with alert status
- `/unlink` - Unlink your Telegram account
- `/help` - Show available commands

**Linking Your Account**:

1. Log in to FilterBets web app
2. Go to Settings page
3. Click "Link Telegram" button
4. You'll be redirected to Telegram
5. Click "Start" in the bot chat
6. Your account is now linked!

### Local Development

```bash
# Install all dependencies
make install

# Run backend (in one terminal)
make dev-b

# Run frontend (in another terminal)
make dev-f
```

## Available Commands

```bash
# Docker
make up          # Start all services
make down        # Stop all services
make build       # Build Docker images
make logs        # View all logs

# Development
make install     # Install dependencies
make dev-b       # Run backend locally
make dev-f       # Run frontend locally

# Database
make migrate     # Run migrations
make makemigrations MSG="description"  # Create migration

# Quality
make test        # Run all tests
make lint        # Run all linters
make format      # Format code
make typecheck   # Type checking
```

## Project Structure

```text
filterbets/
├── backend/           # FastAPI backend
│   ├── app/           # Application code
│   ├── alembic/       # Database migrations
│   └── tests/         # Backend tests
├── frontend/          # React frontend
│   ├── src/
│   │   ├── api/       # API client
│   │   ├── components/# React components
│   │   └── pages/     # Page components
│   └── public/        # Static assets
├── data/              # Data files (gitignored)
├── docs/              # Documentation
└── tasks/             # PRDs and task lists
```

## Development Workflow

1. Create a PRD using `agent-template/create-prd.md`
2. Generate tasks using `agent-template/generate-tasks.md`
3. Implement tasks step by step
4. Run `./git_workflow_orchestrator.py feat` to verify and commit

## API Documentation

Once the backend is running, visit:

- Swagger UI: <http://localhost:8000/docs>
- ReDoc: <http://localhost:8000/redoc>

## License

MIT
