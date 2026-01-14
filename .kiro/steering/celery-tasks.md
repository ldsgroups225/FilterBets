---
inclusion: fileMatch
fileMatchPattern: "backend/app/tasks/**/*.py"
---

# Celery Background Tasks

## Task Structure

### Basic Task Template

```python
import logging
from typing import Any

from app.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.my_tasks.my_task", bind=True)
def my_task(self: Any, param1: str, param2: int) -> dict[str, Any]:
    """
    Task description.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Dictionary with task results
    """
    try:
        # Task logic here
        result = do_something(param1, param2)

        logger.info(f"Task completed successfully: {result}")
        return {"status": "success", "result": result}

    except Exception as e:
        logger.error(f"Task failed: {e}")
        raise
```

### Async Task with Database Access

```python
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.config import get_settings

settings = get_settings()


def get_async_session() -> AsyncSession:
    """Create async database session for Celery tasks."""
    engine = create_async_engine(settings.database_url, echo=False)
    async_session_maker = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    return async_session_maker()


@celery_app.task(name="app.tasks.backtest_tasks.run_async_backtest", bind=True)
def run_async_backtest(self: Any, job_id: str, filter_id: int) -> dict[str, Any]:
    """Run backtest asynchronously."""

    async def _run():
        session = get_async_session()
        try:
            # Async database operations
            result = await do_async_work(session, job_id, filter_id)
            return result
        finally:
            await session.close()

    return asyncio.run(_run())
```

## Celery Configuration

### celery_app.py

```python
from celery import Celery
from celery.schedules import crontab

from app.config import get_settings

settings = get_settings()

celery_app = Celery(
    "filterbets",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=[
        "app.tasks.stats_tasks",
        "app.tasks.backtest_tasks",
    ],
)

celery_app.conf.update(
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max
    task_soft_time_limit=3300,  # 55 min soft limit
    result_expires=86400,  # 24 hours
    accept_content=["json"],
    task_serializer="json",
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# Scheduled tasks (Celery Beat)
celery_app.conf.beat_schedule = {
    "refresh-team-stats-daily": {
        "task": "app.tasks.stats_tasks.refresh_all_team_stats_task",
        "schedule": crontab(hour=2, minute=0),  # 2 AM UTC daily
    },
}

# Task routing
celery_app.conf.task_routes = {
    "app.tasks.stats_tasks.*": {"queue": "stats"},
    "app.tasks.backtest_tasks.*": {"queue": "backtest"},
}
```

## Task Patterns

### Progress Tracking

```python
@celery_app.task(bind=True)
def long_running_task(self: Any, job_id: str) -> dict:
    total_steps = 100

    for step in range(total_steps):
        # Update progress
        self.update_state(
            state="PROGRESS",
            meta={"current": step, "total": total_steps}
        )
        do_step(step)

    return {"status": "completed", "total_steps": total_steps}
```

### Error Handling with Retries

```python
@celery_app.task(
    bind=True,
    autoretry_for=(ConnectionError, TimeoutError),
    retry_backoff=True,
    retry_backoff_max=600,
    max_retries=3,
)
def task_with_retry(self: Any, data: dict) -> dict:
    try:
        return process_data(data)
    except ValueError as e:
        # Don't retry for validation errors
        logger.error(f"Validation error: {e}")
        raise
```

### Chaining Tasks

```python
from celery import chain

# Execute tasks in sequence
result = chain(
    fetch_data.s(source_id),
    process_data.s(),
    save_results.s(destination_id),
)()
```

## Running Celery

### Development

```bash
# Start worker
cd backend
poetry run celery -A app.tasks.celery_app worker --loglevel=info

# Start beat scheduler
poetry run celery -A app.tasks.celery_app beat --loglevel=info

# Start both (for development)
poetry run celery -A app.tasks.celery_app worker --beat --loglevel=info
```

### Production (Docker)

```yaml
# docker-compose.yml
celery-worker:
  build: ./backend
  command: celery -A app.tasks.celery_app worker --loglevel=info
  depends_on:
    - redis
    - db

celery-beat:
  build: ./backend
  command: celery -A app.tasks.celery_app beat --loglevel=info
  depends_on:
    - redis
```

## Monitoring

### Flower (Celery monitoring)

```bash
poetry run celery -A app.tasks.celery_app flower --port=5555
```

### Task Status Check

```python
from celery.result import AsyncResult

def get_task_status(task_id: str) -> dict:
    result = AsyncResult(task_id)
    return {
        "task_id": task_id,
        "status": result.status,
        "result": result.result if result.ready() else None,
    }
```
