# Tasks: Phase 5 - Notifications & Pre-Match Scanner

## Relevant Files

- `backend/app/config.py` - Add Telegram bot token and scanner configuration settings
- `backend/app/models/user.py` - Already has telegram fields, may need scan_frequency
- `backend/app/models/filter.py` - Ensure alerts_enabled field exists
- `backend/app/models/filter_match.py` - New model for tracking notified matches
- `backend/app/schemas/telegram.py` - New schemas for Telegram linking endpoints
- `backend/app/schemas/notification.py` - New schemas for notification history
- `backend/app/schemas/scanner.py` - New schemas for scanner status
- `backend/app/api/v1/telegram.py` - New router for Telegram linking endpoints
- `backend/app/api/v1/scanner.py` - New router for scanner endpoints
- `backend/app/api/v1/notifications.py` - New router for notification history
- `backend/app/services/telegram_service.py` - New service for Telegram operations
- `backend/app/services/scanner_service.py` - New service for pre-match scanning
- `backend/app/tasks/celery_app.py` - Update with scanner schedule and notification queue
- `backend/app/tasks/scanner_tasks.py` - New Celery tasks for scanning
- `backend/app/tasks/notification_tasks.py` - New Celery tasks for sending notifications
- `backend/app/bot/telegram_bot.py` - New Telegram bot implementation
- `backend/app/bot/__init__.py` - Bot module init
- `backend/alembic/versions/xxx_add_filter_matches.py` - Migration for filter_matches table
- `backend/alembic/versions/xxx_add_scan_frequency.py` - Migration for user scan_frequency
- `backend/tests/test_telegram.py` - Tests for Telegram linking
- `backend/tests/test_scanner.py` - Tests for scanner service
- `backend/tests/test_notification_tasks.py` - Tests for notification tasks
- `frontend/src/pages/Settings.tsx` - Add Telegram linking UI
- `frontend/src/components/TelegramLinkButton.tsx` - New component for linking
- `frontend/src/services/api/telegram.ts` - API client for Telegram endpoints
- `frontend/src/hooks/useTelegramStatus.ts` - Hook for Telegram status

### Notes

- Unit tests should be placed in `backend/tests/` directory
- Use `cd backend && poetry run pytest tests/ -v` to run backend tests
- The Telegram bot runs as a separate process, not inside FastAPI
- Redis is used for storing temporary link tokens (30-min TTL)

## Instructions for Completing Tasks

**IMPORTANT:** As you complete each task, you must check it off in this markdown file by changing `- [ ]` to `- [x]`. This helps track progress and ensures you don't skip any steps.

Example:

- `- [ ] 1.1 Read file` → `- [x] 1.1 Read file` (after completing)

Update the file after completing each sub-task, not just after completing an entire parent task.

## Tasks

- [x] 0.0 Create feature branch
  - [x] 0.1 Create and checkout a new branch: `git checkout -b feature/phase5-notifications-scanner`

- [x] 1.0 Database & Model Updates
  - [x] 1.1 Add `scan_frequency` field to User model (enum: '2x', '4x', '6x', default '2x')
  - [x] 1.2 Create `FilterMatch` model in `backend/app/models/filter_match.py` with fields: id, filter_id, fixture_id, matched_at, notification_sent, bet_result
  - [x] 1.3 Add unique constraint on (filter_id, fixture_id) in FilterMatch model
  - [x] 1.4 Ensure `alerts_enabled` field exists on Filter model (check and add if missing)
  - [x] 1.5 Create Alembic migration for FilterMatch table and User.scan_frequency
  - [x] 1.6 Run migration and verify schema: `cd backend && poetry run alembic upgrade head`

- [x] 2.0 Telegram Deep Link Authentication
  - [x] 2.1 Add Telegram config settings to `backend/app/config.py`: bot_token, bot_username, link_token_ttl
  - [x] 2.2 Create `backend/app/services/telegram_service.py` with TelegramService class
  - [x] 2.3 Implement `generate_link_token()` - creates UUID token, stores in Redis with 30-min TTL
  - [x] 2.4 Implement `validate_link_token()` - validates token exists and not expired
  - [x] 2.5 Implement `link_telegram_account()` - links chat_id to user, deletes token, sets telegram_verified=True
  - [x] 2.6 Implement `unlink_telegram_account()` - clears telegram_chat_id and telegram_verified
  - [x] 2.7 Implement `get_deep_link_url()` - returns `https://t.me/{bot_username}?start={token}`

- [x] 3.0 Telegram Bot Implementation
  - [x] 3.1 Add `python-telegram-bot>=20.0` to backend dependencies in pyproject.toml
  - [x] 3.2 Create `backend/app/bot/__init__.py` module
  - [x] 3.3 Create `backend/app/bot/telegram_bot.py` with bot application setup
  - [x] 3.4 Implement `/start {token}` handler - validates token, links account, sends confirmation
  - [x] 3.5 Implement `/start` handler (no token) - sends welcome message with instructions
  - [x] 3.6 Implement `/status` handler - shows linked account email (masked) and active filter count
  - [x] 3.7 Implement `/filters` handler - lists user's active filters with alert status
  - [x] 3.8 Implement `/unlink` handler - unlinks Telegram from account with confirmation
  - [x] 3.9 Implement `/help` handler - shows available commands
  - [x] 3.10 Create `backend/app/bot/run_bot.py` entry point script for running bot as separate process
  - [x] 3.11 Add bot service to docker-compose.yml

- [x] 4.0 Pre-Match Scanner Service
  - [x] 4.1 Create `backend/app/services/scanner_service.py` with PreMatchScanner class
  - [x] 4.2 Implement `get_upcoming_fixtures()` - fetches fixtures in next N hours (configurable)
  - [x] 4.3 Implement `get_users_with_active_alerts()` - fetches users with verified Telegram and active filter alerts
  - [x] 4.4 Implement `scan_filters_for_user()` - applies user's filters to upcoming fixtures using FilterEngine
  - [x] 4.5 Implement `get_new_matches()` - filters out already-notified filter+fixture combinations
  - [x] 4.6 Implement `record_filter_match()` - inserts into filter_matches table
  - [x] 4.7 Implement `run_full_scan()` - orchestrates full scan for all users, returns scan stats
  - [x] 4.8 Add scanner config to settings: lookahead_hours, max_notifications_per_scan

- [ ] 5.0 Notification System
  - [ ] 5.1 Create `backend/app/tasks/notification_tasks.py` module
  - [ ] 5.2 Implement `format_notification_message()` - formats match data into Telegram message template
  - [ ] 5.3 Implement `send_filter_alert` Celery task - sends single notification via Telegram API
  - [ ] 5.4 Add rate limiting logic (max 30 msgs/sec) using Redis token bucket
  - [ ] 5.5 Implement retry logic with exponential backoff for failed sends
  - [ ] 5.6 Update FilterMatch.notification_sent on successful delivery
  - [ ] 5.7 Create `backend/app/tasks/scanner_tasks.py` with `run_pre_match_scanner` task
  - [ ] 5.8 Update `backend/app/tasks/celery_app.py` - add scanner schedule (2x, 4x, 6x daily options)
  - [ ] 5.9 Add notification_tasks to Celery include list
  - [ ] 5.10 Configure task routing: scanner tasks to 'scanner' queue, notification tasks to 'notifications' queue

- [ ] 6.0 API Endpoints
  - [ ] 6.1 Create `backend/app/schemas/telegram.py` - TelegramLinkResponse, TelegramStatusResponse
  - [ ] 6.2 Create `backend/app/schemas/notification.py` - NotificationHistoryItem, NotificationListResponse
  - [ ] 6.3 Create `backend/app/schemas/scanner.py` - ScannerStatusResponse, ScanTriggerResponse
  - [ ] 6.4 Create `backend/app/api/v1/telegram.py` router
  - [ ] 6.5 Implement `POST /auth/telegram/generate-link` - generates deep link URL for current user
  - [ ] 6.6 Implement `GET /auth/telegram/status` - returns Telegram link status
  - [ ] 6.7 Implement `DELETE /auth/telegram/unlink` - unlinks Telegram account
  - [ ] 6.8 Create `backend/app/api/v1/notifications.py` router
  - [ ] 6.9 Implement `GET /notifications` - paginated notification history for current user
  - [ ] 6.10 Create `backend/app/api/v1/scanner.py` router
  - [ ] 6.11 Implement `GET /scanner/status` - returns last scan time and stats
  - [ ] 6.12 Implement `POST /scanner/trigger` - manually triggers scan (admin only)
  - [ ] 6.13 Add `PATCH /filters/{id}/alerts` endpoint to filters router - enable/disable alerts
  - [ ] 6.14 Register all new routers in `backend/app/main.py`

- [ ] 7.0 Frontend Telegram Integration
  - [ ] 7.1 Create `frontend/src/services/api/telegram.ts` - API client functions
  - [ ] 7.2 Create `frontend/src/hooks/useTelegramStatus.ts` - hook for fetching/polling status
  - [ ] 7.3 Create `frontend/src/components/TelegramLinkButton.tsx` - button that opens deep link
  - [ ] 7.4 Create `frontend/src/components/TelegramStatus.tsx` - shows linked status with unlink option
  - [ ] 7.5 Update Settings page to include Telegram linking section
  - [ ] 7.6 Add alert toggle to filter list/detail pages
  - [ ] 7.7 Show "Link Telegram first" message if user tries to enable alerts without linked account

- [ ] 8.0 Testing & Documentation
  - [ ] 8.1 Write unit tests for TelegramService (token generation, validation, linking)
  - [ ] 8.2 Write unit tests for PreMatchScanner service
  - [ ] 8.3 Write unit tests for notification formatting
  - [ ] 8.4 Write integration tests for Telegram API endpoints
  - [ ] 8.5 Write integration tests for scanner endpoints
  - [ ] 8.6 Add bot startup instructions to README
  - [ ] 8.7 Document environment variables for Telegram configuration
  - [ ] 8.8 Run full test suite and fix any failures: `cd backend && poetry run pytest tests/ -v`
