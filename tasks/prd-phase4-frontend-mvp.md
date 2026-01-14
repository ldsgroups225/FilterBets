# PRD: Phase 4 - Frontend MVP

## 1. Introduction/Overview

This document outlines the requirements for building the FilterBets frontend MVP - a React-based web application that provides users with a functional interface to interact with the betting analytics platform.

**Problem Statement:** The backend API (Phases 1-3) is complete with authentication, fixtures, filters, and backtesting capabilities, but users have no way to interact with these features. We need a frontend that allows users to create filter strategies, run backtests, and view match data.

**Goal:** Build a functional, desktop-first React frontend that enables users to authenticate, browse fixtures, create betting filters, and run backtests against historical data.

## 2. Goals

1. **Enable User Authentication** - Users can register, login, and maintain authenticated sessions
2. **Provide Data Browsing** - Users can view fixtures, leagues, and team statistics
3. **Support Filter Creation** - Users can create, edit, and manage betting filter strategies
4. **Enable Backtesting** - Users can run backtests on their filters and view performance metrics
5. **Establish UI Foundation** - Set up reusable components and patterns for future development

## 3. User Stories

### Authentication

- **US-1:** As a new user, I want to register an account so I can save my filters and preferences
- **US-2:** As a returning user, I want to login so I can access my saved filters
- **US-3:** As a logged-in user, I want to stay authenticated across page refreshes

### Data Browsing

- **US-4:** As a user, I want to see today's fixtures on the dashboard so I can quickly find matches
- **US-5:** As a user, I want to browse all fixtures with filters (date, league) so I can find specific matches
- **US-6:** As a user, I want to view fixture details including team stats so I can make informed decisions

### Filter Management

- **US-7:** As a user, I want to create a new filter with multiple criteria so I can define my betting strategy
- **US-8:** As a user, I want to see a list of my saved filters so I can manage them
- **US-9:** As a user, I want to edit or delete my filters so I can refine my strategies
- **US-10:** As a user, I want to see which fixtures match my filter so I can identify opportunities

### Backtesting

- **US-11:** As a user, I want to run a backtest on my filter so I can evaluate its historical performance
- **US-12:** As a user, I want to see backtest results (win rate, ROI, streaks) so I can assess strategy viability
- **US-13:** As a user, I want to choose which seasons to include in my backtest

## 4. Functional Requirements

### 4.1 Project Setup

1. The application must be built with React 18+ and TypeScript
2. The application must use Vite as the build tool
3. The application must use TanStack Query for server state management
4. The application must use TanStack Table for data tables
5. The application must use Tailwind CSS for styling
6. The application must use shadcn/ui for UI components
7. The application must use React Router v6 for navigation

### 4.2 Authentication

1. The system must provide a login page at `/login`
2. The system must provide a registration page at `/register`
3. The system must store JWT tokens securely (httpOnly cookies or secure localStorage)
4. The system must automatically refresh tokens before expiry
5. The system must redirect unauthenticated users to login
6. The system must display the current user's email in the header when logged in
7. The system must provide a logout button that clears the session

### 4.3 Layout & Navigation

1. The application must have a consistent header with navigation links
2. The application must have a sidebar for main navigation (Dashboard, Fixtures, Filters)
3. The application must show loading states during data fetching
4. The application must show error states when API calls fail
5. The application must be usable on desktop screens (1024px+)
6. The application should have basic mobile responsiveness (collapsible sidebar)

### 4.4 Dashboard Page

1. The dashboard must display at route `/`
2. The dashboard must show today's fixtures count
3. The dashboard must show the user's active filters count
4. The dashboard must show a quick list of today's matches (max 10)
5. The dashboard must provide quick links to create a new filter

### 4.5 Fixtures Pages

1. The fixtures list must display at route `/fixtures`
2. The fixtures list must show matches in a paginated table
3. The fixtures list must allow filtering by date range
4. The fixtures list must allow filtering by league
5. The fixtures list must show: date, home team, away team, score (if finished), league
6. The fixture detail page must display at route `/fixtures/:id`
7. The fixture detail must show match information and team statistics

### 4.6 Filters Pages

1. The filters list must display at route `/filters`
2. The filters list must show all user's filters with name, status, and created date
3. The filter creation page must display at route `/filters/new`
4. The filter edit page must display at route `/filters/:id/edit`
5. The filter detail page must display at route `/filters/:id`

### 4.7 Filter Builder

1. The filter builder must allow selecting a bet type (home_win, away_win, draw, over_2_5, under_2_5)
2. The filter builder must allow adding multiple filter rules (conditions)
3. Each rule must have: field selector, operator selector, value input
4. The filter builder must support these operators: =, !=, >, <, >=, <=, in, between
5. The filter builder must validate rules before saving
6. The filter builder must show a preview count of matching fixtures
7. The filter builder must allow naming and describing the filter

### 4.8 Backtest Feature

1. The filter detail page must have a "Run Backtest" button
2. The backtest form must allow selecting seasons to test against
3. The backtest form must allow setting a stake amount
4. The backtest results must show: total matches, wins, losses, win rate
5. The backtest results must show: total profit, ROI percentage
6. The backtest results must show: longest winning/losing streaks
7. The backtest results must show a monthly breakdown table
8. The system must show a loading indicator during backtest execution

### 4.9 API Integration

1. The application must use a centralized API client with base URL configuration
2. The application must automatically attach JWT tokens to authenticated requests
3. The application must handle 401 responses by redirecting to login
4. The application must use TanStack Query for caching and refetching

## 5. Non-Goals (Out of Scope)

The following are explicitly NOT part of this MVP:

1. **Telegram Integration UI** - Settings page for Telegram linking (Phase 5)
2. **Real-time Updates** - WebSocket connections for live scores/odds
3. **Social Features** - Public filters, trending filters, user following
4. **Mobile App** - Native mobile or PWA features
5. **Dark Mode** - Theme switching (can use system default)
6. **Internationalization** - Multi-language support
7. **Advanced Analytics** - Charts, graphs, profit curves (basic tables only)
8. **Team/League Detail Pages** - Dedicated pages for teams and leagues
9. **User Profile/Settings** - Profile editing, password change
10. **Notifications** - In-app notification center

## 6. Design Considerations

### UI Components (shadcn/ui)

Use these shadcn/ui components as the foundation:

- `Button`, `Input`, `Label` - Form elements
- `Card` - Content containers
- `Table` - Data display
- `Select`, `Combobox` - Dropdowns
- `Dialog`, `Sheet` - Modals and sidebars
- `Tabs` - Content organization
- `Badge` - Status indicators
- `Skeleton` - Loading states
- `Toast` - Notifications

### Color Scheme

- Primary: Blue (trust, analytics)
- Success: Green (winning bets)
- Danger: Red (losing bets)
- Neutral: Gray scale for text and backgrounds

### Layout Structure

```text
┌─────────────────────────────────────────────┐
│  Header (Logo, Nav, User Menu)              │
├──────────┬──────────────────────────────────┤
│          │                                  │
│ Sidebar  │  Main Content Area               │
│ (Nav)    │                                  │
│          │                                  │
│          │                                  │
└──────────┴──────────────────────────────────┘
```

## 7. Technical Considerations

### Project Structure

```text
frontend/
├── src/
│   ├── components/
│   │   ├── ui/              # shadcn/ui components
│   │   ├── layout/          # Header, Sidebar, Layout
│   │   ├── filters/         # Filter-related components
│   │   └── fixtures/        # Fixture-related components
│   ├── pages/               # Route pages
│   ├── hooks/               # Custom React hooks
│   ├── services/            # API client
│   ├── types/               # TypeScript types
│   ├── lib/                 # Utilities
│   └── App.tsx
├── package.json
└── vite.config.ts
```

### API Endpoints to Integrate

From the existing backend:

- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Token refresh
- `GET /api/v1/auth/me` - Current user
- `GET /api/v1/fixtures` - List fixtures
- `GET /api/v1/fixtures/:id` - Fixture detail
- `GET /api/v1/fixtures/today` - Today's fixtures
- `GET /api/v1/leagues` - List leagues
- `GET /api/v1/filters` - List user's filters
- `POST /api/v1/filters` - Create filter
- `GET /api/v1/filters/:id` - Filter detail
- `PUT /api/v1/filters/:id` - Update filter
- `DELETE /api/v1/filters/:id` - Delete filter
- `GET /api/v1/filters/:id/matches` - Matching fixtures
- `POST /api/v1/filters/:id/backtest` - Run backtest

### Dependencies

```json
{
  "dependencies": {
    "react": "^18.x",
    "react-dom": "^18.x",
    "react-router-dom": "^6.x",
    "@tanstack/react-query": "^5.x",
    "@tanstack/react-table": "^8.x",
    "axios": "^1.x",
    "tailwindcss": "^3.x",
    "class-variance-authority": "^0.x",
    "clsx": "^2.x",
    "lucide-react": "^0.x",
    "date-fns": "^3.x",
    "zod": "^3.x",
    "react-hook-form": "^7.x",
    "@hookform/resolvers": "^3.x"
  }
}
```

## 8. Success Metrics

1. **Functional Completeness** - All 54 functional requirements implemented
2. **API Integration** - All backend endpoints successfully integrated
3. **Error Handling** - No unhandled errors in console during normal usage
4. **Load Time** - Initial page load under 3 seconds
5. **Usability** - A user can complete the full flow: register → create filter → run backtest

## 9. Open Questions

1. **Authentication Storage** - Should we use httpOnly cookies (more secure) or localStorage (simpler)?
   - *Recommendation: localStorage for MVP simplicity, migrate to cookies later*

2. **Filter Field Options** - Should field options be hardcoded or fetched from backend?
   - *Recommendation: Hardcode for MVP based on existing schema*

3. **Backtest Async Handling** - Should we poll for async backtest results or use the sync endpoint?
   - *Recommendation: Use sync endpoint for MVP (already implemented), add async later for large backtests*

---

*Document created: January 14, 2026*
*Phase: 4 of 6*
*Estimated Duration: 2 weeks*
