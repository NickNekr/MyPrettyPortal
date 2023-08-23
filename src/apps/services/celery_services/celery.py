from celery import Celery

from config import app_config

celery_app = Celery(
    "duplication",
)

celery_app.config_from_object(app_config.CeleryConfig)
