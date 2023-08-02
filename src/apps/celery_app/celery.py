from celery import Celery
from celery.schedules import crontab

from config import app_config

celery_app = Celery(
    "duplication",
    broker="redis://redis:6379/0",
    include=[
        "celery_app.tasks",
    ],
)

celery_app.conf.beat_schedule = {
    "my-scheduled-task": {
        "task": "celery_app.tasks.update_data",
        "schedule": crontab(minute="0", hour="9"),
    },
}

celery_app.conf.broker_connection_retry_on_startup = True
celery_app.conf.timezone = app_config.TZ
celery_app.conf.beat_schedule_timezone = app_config.TZ

if __name__ == "__main__":
    celery_app.start()
