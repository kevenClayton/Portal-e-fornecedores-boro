from celery import Celery
from app.config import settings

# Create Celery instance
celery_app = Celery(
    "portal_automation",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.tasks"]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="America/Sao_Paulo",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    broker_connection_retry_on_startup=True,
)

# Beat schedule for periodic tasks
celery_app.conf.beat_schedule = {
    "process-portal-routes": {
        "task": "app.tasks.process_portal_routes",
        "schedule": settings.task_interval_minutes * 60,  # Convert minutes to seconds
    },
}

if __name__ == "__main__":
    celery_app.start()
