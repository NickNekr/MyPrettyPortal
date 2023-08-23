import logging
import traceback

from .celery import celery_app
from apps.services.celery_services.duplication.update_state import update_database
from apps.services.redis_services.red import redis_client


@celery_app.task
def update_data():
    lock = redis_client.conn.setnx("update_task_lock", "locked")
    if lock:
        try:
            update_database()
        except Exception:
            logging.error(traceback.format_exc())
        finally:
            redis_client.conn.delete("update_task_lock")
    else:
        pass
