# FilterBets Frontend

React TypeScript frontend for the FilterBets betting analytics platform.

## Tech Stack

- **Framework:** React 18+ with TypeScript
- **Build Tool:** Vite (Rolldown)
- **Styling:** Tailwind CSS 4.x
- **UI Components:** shadcn/ui (Base UI)
- **Data Fetching:** TanStack Query v5
- **Tables:** TanStack Table v8
- **Routing:** React Router v7
- **HTTP Client:** Axios
- **Icons:** Tabler Icons
- **Package Manager:** pnpm

## Getting Started

### Prerequisites

- Node.js 18+ or 20+
- pnpm 8+

### Installation

```bash
# Install dependencies
pnpm install
```

### Development

```bash
# Start development server (http://localhost:5173)
pnpm dev

# Run type checking
pnpm typecheck

# Run linting
pnpm lint

# Fix linting issues
pnpm lint:fix

# Run tests
pnpm test

# Run tests in watch mode
pnpm test:watch

# Run tests with coverage
pnpm test:coverage
```

### Build

```bash
# Build for production
pnpm build

# Preview production build
pnpm preview
```

## Project Structure

```text
frontend/
├── src/
│   ├── api/              # API client configuration
│   ├── components/       # React components
│   │   ├── filters/      # Filter-related components
│   │   ├── fixtures/     # Fixture-related components
│   │   ├── layout/       # Layout components (Header, Sidebar, etc.)
│   │   └── ui/           # shadcn/ui components
│   ├── contexts/         # React contexts (Auth, etc.)
│   ├── hooks/            # Custom React hooks
│   ├── lib/              # Utility libraries
│   ├── pages/            # Page components
│   ├── services/         # API service functions
│   ├── styles/           # Global styles
│   └── types/            # TypeScript type definitions
├── public/               # Static assets
└── tests/                # Test files
```

## Key Features

### Authentication

- JWT-based authentication with auto-refresh
- Protected routes with auth guards
- Login and registration pages

### Dashboard

- Today's fixtures overview
- Active filters count
- Quick actions for creating filters

### Fixtures

- Searchable and filterable fixtures list
- Date range and league filters
- Detailed fixture view with odds and team stats
- Responsive table with pagination

### Filters

- Create and manage betting filter strategies
- Dynamic rule builder with field/operator/value inputs
- Filter activation/deactivation
- Delete with confirmation

### Backtesting

- Run backtests against historical data
- Comprehensive results with analytics
- Win/loss/push breakdown
- Streak analysis and drawdown metrics
- Monthly performance breakdown

## Environment Variables

Create a `.env` file in the frontend directory:

```env
VITE_API_BASE_URL=http://localhost:8000
```

## Code Style

- **Components:** PascalCase (e.g., `FilterBuilder.tsx`)
- **Hooks:** camelCase with `use` prefix (e.g., `useFilters.ts`)
- **Types:** PascalCase (e.g., `Filter`, `BacktestResponse`)
- **Functions:** camelCase (e.g., `getFilters`, `runBacktest`)

## Testing

Tests are written using Vitest and React Testing Library:

```bash
# Run all tests
pnpm test

# Run tests in watch mode
pnpm test:watch

# Generate coverage report
pnpm test:coverage
```

## Adding shadcn/ui Components

```bash
# Add a new component
pnpm dlx shadcn@latest add <component-name>

# Example: Add dialog component
pnpm dlx shadcn@latest add dialog
```

## API Integration

The frontend communicates with the FastAPI backend at `http://localhost:8000` (configurable via `VITE_API_BASE_URL`).

### API Endpoints Used

- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/refresh` - Token refresh
- `GET /api/v1/fixtures` - List fixtures
- `GET /api/v1/fixtures/today` - Today's fixtures
- `GET /api/v1/fixtures/:id` - Get fixture details
- `GET /api/v1/filters` - List user's filters
- `POST /api/v1/filters` - Create filter
- `PUT /api/v1/filters/:id` - Update filter
- `DELETE /api/v1/filters/:id` - Delete filter
- `POST /api/v1/filters/:id/backtest` - Run backtest

## Troubleshooting

### Port Already in Use

If port 5173 is already in use, Vite will automatically try the next available port.

### API Connection Issues

Ensure the backend is running at `http://localhost:8000` and the `VITE_API_BASE_URL` environment variable is set correctly.

### Build Warnings

The build may show warnings about chunk sizes. This is expected for the initial MVP. Code splitting can be implemented in future iterations.

## License

This project is part of the FilterBets platform.
