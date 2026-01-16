# PRD: Phase 5 - Notifications & Pre-Match Scanner

## Introduction/Overview

Phase 5 implements the notification system and automated pre-match scanner for FilterBets. This phase enables users to receive real-time Telegram alerts when upcoming matches meet their filter criteria, transforming FilterBets from a manual analysis tool into an automated betting assistant.

The system consists of three main components:

1. **Celery Infrastructure** - Enhanced background task processing with scheduled jobs
2. **Telegram Bot** - Handles user linking and sends match notifications
3. **Pre-Match Scanner** - Automatically evaluates upcoming fixtures against active user filters

## Goals

1. Enable users to link their Telegram account with one-click deep linking
2. Automatically scan upcoming matches against user-defined filters at configurable intervals
3. Send formatted Telegram notifications with match info, key stats, and odds
4. Prevent duplicate notifications for the same filter + fixture combination
5. Support premium users with configurable scan frequency
6. Track notification history for analytics and debugging

## User Stories

### US-1: Telegram Account Linking

**As a** FilterBets user  
**I want to** link my Telegram account with one click  
**So that** I can receive match notifications on my phone

**Acceptance Criteria:**

- User clicks "Link to Telegram" button in settings
- Browser/app opens Telegram with the FilterBets bot
- Bot automatically links the account using a unique token in the deep link
- User sees confirmation in both Telegram and the web app
- User can unlink their Telegram account at any time

### US-2: Filter Alert Activation

**As a** user with saved filters  
**I want to** enable/disable alerts for specific filters  
**So that** I only get notified for strategies I'm actively using

**Acceptance Criteria:**

- Each filter has an "Enable Alerts" toggle
- Only filters with alerts enabled are included in scanner runs
- User must have linked Telegram to enable alerts
- Disabling alerts stops future notifications but preserves history

### US-3: Receiving Match Notifications

**As a** user with active filter alerts  
**I want to** receive Telegram notifications when matches meet my criteria  
**So that** I don't miss betting opportunities

**Acceptance Criteria:**

- Notification includes: match teams, league, date/time, key stats, odds
- Notification is formatted for easy reading on mobile
- Each filter + fixture combination only triggers one notification (no duplicates)
- Notifications link back to the match details in the app

### US-4: Configurable Scan Frequency (Premium)

**As a** premium user  
**I want to** configure how often my filters are scanned  
**So that** I can get more timely alerts for important matches

**Acceptance Criteria:**

- Free users: scans run twice daily (8 AM and 2 PM UTC)
- Premium users: can choose from 2x, 4x, or 6x daily scans
- Scan frequency is a user-level setting, not per-filter

### US-5: Notification History

**As a** user  
**I want to** see a history of notifications I've received  
**So that** I can track which matches my filters identified

**Acceptance Criteria:**

- View list of past notifications with match details
- See which filter triggered each notification
- Track bet outcomes (win/loss) for notified matches

## Functional Requirements

### FR-1: Telegram Bot Setup

1. Bot must run as a separate long-running process alongside FastAPI
2. Bot must handle the `/start` command with deep link token for auto-linking
3. Bot must handle `/status` command to check linked account
4. Bot must handle `/filters` command to list active filters
5. Bot must handle `/help` command to show available commands
6. Bot must handle `/unlink` command to disconnect account

### FR-2: Deep Link Account Linking

1. System must generate unique, time-limited tokens (UUID, 30-minute expiry)
2. Deep link format: `https://t.me/filterbet_prematch_spy_bot?start={token}`
3. When user starts bot with token, system must:
   - Validate token exists and is not expired
   - Link the Telegram chat_id to the user account
   - Mark user as `telegram_verified = True`
   - Delete the used token
   - Send confirmation message in Telegram
4. System must store pending link tokens in Redis with TTL

### FR-3: Pre-Match Scanner Service

1. Scanner must fetch upcoming fixtures (configurable lookahead, default 24 hours)
2. Scanner must retrieve all users with:
   - Linked and verified Telegram accounts
   - At least one filter with `alerts_enabled = True`
3. For each user, scanner must:
   - Apply each active filter's rules to upcoming fixtures
   - Identify new matches (not previously notified for this filter)
   - Queue notification tasks for new matches
4. Scanner must record matches in `filter_matches` table with `notification_sent = True`

### FR-4: Notification Task

1. Notification task must format message with:
   - Match: Home Team vs Away Team
   - League name
   - Match date and time (user's timezone if available, else UTC)
   - Key stats: home/away form, H2H if available
   - Odds: home win, draw, away win
   - Link to match in FilterBets app
2. Task must handle Telegram API rate limits (max 30 messages/second)
3. Task must log delivery status and any errors
4. Task must update `filter_matches.notification_sent` on success

### FR-5: Celery Beat Schedule

1. Default schedule: 8:00 AM UTC and 2:00 PM UTC
2. Premium schedules:
   - 4x daily: 6 AM, 11 AM, 4 PM, 9 PM UTC
   - 6x daily: every 4 hours starting at 2 AM UTC
3. Schedule must be configurable via environment variables
4. Each scan must complete within 30 minutes

### FR-6: Duplicate Prevention

1. System must check `filter_matches` table before sending notification
2. Unique constraint: `(filter_id, fixture_id)` combination
3. Once notified, a filter + fixture pair is never re-notified
4. Scanner must skip already-notified combinations efficiently

### FR-7: API Endpoints

1. `POST /api/v1/auth/telegram/generate-link` - Generate deep link URL
2. `GET /api/v1/auth/telegram/status` - Check Telegram link status
3. `DELETE /api/v1/auth/telegram/unlink` - Unlink Telegram account
4. `PATCH /api/v1/filters/{id}/alerts` - Enable/disable filter alerts
5. `GET /api/v1/notifications` - List notification history (paginated)
6. `GET /api/v1/scanner/status` - Get last scan time and stats
7. `POST /api/v1/scanner/trigger` - Manually trigger scan (admin only)

### FR-8: Database Changes

1. Add `telegram_link_tokens` table or use Redis for token storage
2. Add `scan_frequency` field to `users` table (enum: '2x', '4x', '6x')
3. Ensure `filter_matches` table has proper indexes for duplicate checking
4. Add `notification_history` table for detailed tracking (optional)

## Non-Goals (Out of Scope)

1. **Live Scanner** - Real-time in-play match scanning (Phase 6 premium feature)
2. **Multiple Notification Channels** - Email, SMS, push notifications (future)
3. **Custom Notification Templates** - User-defined message formats
4. **Timezone Selection** - All times in UTC for MVP (user timezone in future)
5. **Notification Preferences** - Quiet hours, do-not-disturb settings
6. **Group Chat Support** - Bot only works in private chats for MVP

## Design Considerations

### Telegram Message Format

```text
🎯 FilterBets Alert

Your filter "High-Scoring Home Favorites" matched:

⚽ Manchester United vs Everton
🏆 Premier League
📅 Jan 15, 2026 at 15:00 UTC

📊 Key Stats:
• Man Utd home form: W4 D1 L0
• Everton away form: W1 D2 L2
• H2H last 5: Man Utd 3 wins

💰 Odds:
• Home: 1.85 | Draw: 3.60 | Away: 4.20

🔗 View Match: https://filterbets.com/fixtures/12345
```

### Deep Link Flow

1. User clicks "Link to Telegram" → Frontend calls `POST /auth/telegram/generate-link`
2. Backend generates UUID token, stores in Redis with 30-min TTL, returns deep link URL
3. Frontend redirects to `https://t.me/filterbet_prematch_spy_bot?start={token}`
4. Telegram opens, user clicks "Start"
5. Bot receives `/start {token}`, validates, links account
6. Bot sends confirmation, frontend polls `/auth/telegram/status` to update UI

### Scanner Architecture

```text
[Celery Beat] → triggers → [pre_match_scanner_task]
                                    ↓
                          [Fetch upcoming fixtures]
                                    ↓
                          [For each user with alerts]
                                    ↓
                          [Apply filters to fixtures]
                                    ↓
                          [Queue notification tasks]
                                    ↓
                          [send_filter_alert_task] → [Telegram API]
```

## Technical Considerations

### Dependencies

- `python-telegram-bot>=20.0` - Async Telegram bot library
- Redis - Token storage and Celery broker (already configured)
- Celery Beat - Scheduled task execution (already configured)

### Rate Limiting

- Telegram allows ~30 messages/second per bot
- Implement token bucket or leaky bucket rate limiter
- Queue notifications and process with controlled concurrency

### Error Handling

- Retry failed Telegram sends with exponential backoff
- Log all notification attempts for debugging
- Alert admins if error rate exceeds threshold

### Scalability

- Scanner task should be idempotent (safe to re-run)
- Use database transactions for filter_matches inserts
- Consider sharding scanner by user groups for large user bases

## Success Metrics

1. **Telegram Link Rate** - % of active users who link Telegram (target: 60%)
2. **Alert Activation Rate** - % of filters with alerts enabled (target: 40%)
3. **Notification Delivery Rate** - % of notifications successfully delivered (target: 99%)
4. **Scanner Completion Time** - Time to complete full scan (target: <5 min for 1000 users)
5. **User Engagement** - Click-through rate on notification links (target: 25%)

## Open Questions

1. Should we support multiple Telegram accounts per user?
2. What's the maximum number of active filters per user for free tier?
3. Should notifications include a "Mute this filter" quick action?
4. Do we need webhook fallback if long-polling bot has issues?

---

*Document created: January 14, 2026*
*Phase: 5 of 6*
*Estimated effort: 2 weeks*
