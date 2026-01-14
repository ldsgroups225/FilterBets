# Tasks: Phase 4 - Frontend MVP

## Relevant Files

### Configuration

- `frontend/package.json` - Dependencies and scripts
- `frontend/vite.config.ts` - Vite configuration
- `frontend/tailwind.config.js` - Tailwind configuration
- `frontend/tsconfig.json` - TypeScript configuration
- `frontend/components.json` - shadcn/ui configuration

### Core Application

- `frontend/src/App.tsx` - Main application component
- `frontend/src/main.tsx` - Application entry point
- `frontend/src/index.css` - Global styles

### Layout Components

- `frontend/src/components/layout/Header.tsx` - Top navigation header
- `frontend/src/components/layout/Sidebar.tsx` - Side navigation
- `frontend/src/components/layout/Layout.tsx` - Main layout wrapper
- `frontend/src/components/layout/ProtectedRoute.tsx` - Auth guard

### Pages

- `frontend/src/pages/LoginPage.tsx` - Login page
- `frontend/src/pages/RegisterPage.tsx` - Registration page
- `frontend/src/pages/DashboardPage.tsx` - Dashboard/home page
- `frontend/src/pages/FixturesPage.tsx` - Fixtures list page
- `frontend/src/pages/FixtureDetailPage.tsx` - Single fixture page
- `frontend/src/pages/FiltersPage.tsx` - Filters list page
- `frontend/src/pages/FilterDetailPage.tsx` - Single filter page
- `frontend/src/pages/FilterBuilderPage.tsx` - Create/edit filter page

### Feature Components

- `frontend/src/components/filters/FilterBuilder.tsx` - Filter creation form
- `frontend/src/components/filters/RuleRow.tsx` - Single filter rule
- `frontend/src/components/filters/BacktestForm.tsx` - Backtest configuration
- `frontend/src/components/filters/BacktestResults.tsx` - Backtest display
- `frontend/src/components/fixtures/FixturesTable.tsx` - Fixtures data table
- `frontend/src/components/fixtures/FixtureCard.tsx` - Fixture summary card

### Services & Hooks

- `frontend/src/services/api.ts` - API client configuration
- `frontend/src/services/auth.ts` - Auth API functions
- `frontend/src/services/fixtures.ts` - Fixtures API functions
- `frontend/src/services/filters.ts` - Filters API functions
- `frontend/src/hooks/useAuth.ts` - Authentication hook
- `frontend/src/hooks/useFilters.ts` - Filters data hooks
- `frontend/src/hooks/useFixtures.ts` - Fixtures data hooks

### Types

- `frontend/src/types/auth.ts` - Auth types
- `frontend/src/types/fixture.ts` - Fixture types
- `frontend/src/types/filter.ts` - Filter types
- `frontend/src/types/api.ts` - API response types

### Notes

- Run frontend: `cd frontend && pnpm dev`
- Run tests: `cd frontend && pnpm test`
- Build: `cd frontend && pnpm build`
- Add shadcn component: `cd frontend && pnpm dlx shadcn@latest add <component>`

## Instructions for Completing Tasks

**IMPORTANT:** As you complete each task, check it off by changing `- [ ]` to `- [x]`.

## Tasks

- [x] 0.0 Create feature branch
  - [x] 0.1 Create and checkout branch `feature/phase4-frontend-mvp`

- [x] 1.0 Project Setup & Configuration
  - [x] 1.1 Initialize Vite + React + TypeScript project in `frontend/`
  - [x] 1.2 Configure Tailwind CSS with custom theme colors
  - [x] 1.3 Initialize shadcn/ui and add base components (button, input, card, table)
  - [x] 1.4 Configure TanStack Query provider
  - [x] 1.5 Set up React Router with route definitions
  - [x] 1.6 Create API client with axios and interceptors
  - [x] 1.7 Set up environment variables (.env) for API base URL
  - [x] 1.8 Add additional shadcn components (select, dialog, sheet, tabs, badge, skeleton, toast)

- [ ] 2.0 Authentication System
  - [ ] 2.1 Create auth types (User, LoginRequest, RegisterRequest, AuthResponse)
  - [ ] 2.2 Create auth API service functions (login, register, refresh, getMe)
  - [ ] 2.3 Create AuthContext with user state and auth methods
  - [ ] 2.4 Create useAuth hook for accessing auth context
  - [ ] 2.5 Implement token storage and auto-refresh logic
  - [ ] 2.6 Create ProtectedRoute component for auth guards
  - [ ] 2.7 Create LoginPage with form validation
  - [ ] 2.8 Create RegisterPage with form validation
  - [ ] 2.9 Add 401 response interceptor to redirect to login
  - [ ] 2.10 Test authentication flow end-to-end

- [ ] 3.0 Layout & Navigation
  - [ ] 3.1 Create Header component with logo and user menu
  - [ ] 3.2 Create Sidebar component with navigation links
  - [ ] 3.3 Create Layout component combining Header and Sidebar
  - [ ] 3.4 Add responsive sidebar (collapsible on mobile)
  - [ ] 3.5 Create loading spinner component
  - [ ] 3.6 Create error boundary component
  - [ ] 3.7 Style active navigation links

- [ ] 4.0 Dashboard Page
  - [ ] 4.1 Create DashboardPage component
  - [ ] 4.2 Create stats cards (today's fixtures, active filters)
  - [ ] 4.3 Create today's matches list component
  - [ ] 4.4 Add quick action buttons (create filter, view all fixtures)
  - [ ] 4.5 Integrate with fixtures API (today's fixtures)
  - [ ] 4.6 Integrate with filters API (user's filters count)

- [ ] 5.0 Fixtures Feature
  - [ ] 5.1 Create fixture types (Fixture, FixtureListResponse)
  - [ ] 5.2 Create fixtures API service functions
  - [ ] 5.3 Create useFixtures hook with TanStack Query
  - [ ] 5.4 Create FixturesTable component with TanStack Table
  - [ ] 5.5 Add pagination to fixtures table
  - [ ] 5.6 Add date range filter to fixtures page
  - [ ] 5.7 Add league filter dropdown to fixtures page
  - [ ] 5.8 Create FixturesPage combining filters and table
  - [ ] 5.9 Create FixtureDetailPage with match info
  - [ ] 5.10 Display team statistics on fixture detail

- [ ] 6.0 Filters List & Management
  - [ ] 6.1 Create filter types (Filter, FilterRule, CreateFilterRequest)
  - [ ] 6.2 Create filters API service functions (list, get, create, update, delete)
  - [ ] 6.3 Create useFilters hooks with TanStack Query
  - [ ] 6.4 Create FiltersPage with filters list
  - [ ] 6.5 Create filter card component showing name, status, rule count
  - [ ] 6.6 Add delete filter functionality with confirmation
  - [ ] 6.7 Add toggle active/inactive filter functionality
  - [ ] 6.8 Create FilterDetailPage showing filter info and matches

- [ ] 7.0 Filter Builder
  - [ ] 7.1 Define filter field options (field name, type, operators)
  - [ ] 7.2 Create RuleRow component (field, operator, value inputs)
  - [ ] 7.3 Create FilterBuilder component with add/remove rules
  - [ ] 7.4 Implement bet type selector (home_win, away_win, draw, over_2_5, under_2_5)
  - [ ] 7.5 Implement dynamic value inputs based on field type
  - [ ] 7.6 Add form validation with zod and react-hook-form
  - [ ] 7.7 Create FilterBuilderPage for new filters
  - [ ] 7.8 Create filter edit mode (pre-populate form)
  - [ ] 7.9 Add matching fixtures preview count
  - [ ] 7.10 Test filter creation end-to-end

- [ ] 8.0 Backtest Feature
  - [ ] 8.1 Create backtest types (BacktestRequest, BacktestResponse)
  - [ ] 8.2 Create backtest API service function
  - [ ] 8.3 Create BacktestForm component (seasons, stake inputs)
  - [ ] 8.4 Create BacktestResults component (metrics display)
  - [ ] 8.5 Display win/loss/push counts and win rate
  - [ ] 8.6 Display profit and ROI percentage
  - [ ] 8.7 Display streak information
  - [ ] 8.8 Create monthly breakdown table
  - [ ] 8.9 Add loading state during backtest execution
  - [ ] 8.10 Integrate backtest into FilterDetailPage

- [ ] 9.0 Polish & Testing
  - [ ] 9.1 Add toast notifications for success/error feedback
  - [ ] 9.2 Improve loading states with skeletons
  - [ ] 9.3 Add empty states for lists (no fixtures, no filters)
  - [ ] 9.4 Test all pages on desktop viewport
  - [ ] 9.5 Test basic mobile responsiveness
  - [ ] 9.6 Fix any console errors or warnings
  - [ ] 9.7 Run build and fix any TypeScript errors
  - [ ] 9.8 Update frontend README with setup instructions
  - [ ] 9.9 Commit changes: `feat: add Phase 4 frontend MVP`
