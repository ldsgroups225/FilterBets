"""Celery application configuration."""

from celery import Celery
from celery.schedules import crontab

from app.config import get_settings

settings = get_settings()

# Create Celery app
celery_app = Celery(
    "filterbets",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=[
        "app.tasks.stats_tasks",
        "app.tasks.backtest_tasks",
    ],
)

# Configure Celery
celery_app.conf.update(
    task_track_started=settings.celery_task_track_started,
    task_time_limit=settings.celery_task_time_limit,
    task_soft_time_limit=settings.celery_task_soft_time_limit,
    result_expires=86400,  # 24 hours
    accept_content=["json"],
    task_serializer="json",
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Configure Celery Beat schedule (Task 5.6)
celery_app.conf.beat_schedule = {
    "refresh-team-stats-daily": {
        "task": "app.tasks.stats_tasks.refresh_all_team_stats_task",
        "schedule": crontab(hour=2, minute=0),  # Run daily at 2 AM UTC
        "options": {"expires": 3600},  # Expire after 1 hour if not picked up
    },
}

# Optional: Configure task routes for different queues
celery_app.conf.task_routes = {
    "app.tasks.stats_tasks.*": {"queue": "stats"},
    "app.tasks.backtest_tasks.*": {"queue": "backtest"},
}
