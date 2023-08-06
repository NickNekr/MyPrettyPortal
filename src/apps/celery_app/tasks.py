import logging
import traceback

from .celery import celery_app
from .duplication.update_state import update_database
from apps.redis_app.red import redis_client


# for test
@celery_app.task
def sleep(numbers: int):
    lock = redis_client.setnx("task_lock", "locked")
    if lock:
        import time

        time.sleep(numbers)

        redis_client.delete("task_lock")
    else:
        pass


@celery_app.task
def update_data():
    lock = redis_client.setnx("update_task_lock", "locked")
    if lock:
        try:
            update_database()
        except Exception:
            logging.error(traceback.format_exc())
        finally:
            redis_client.delete("update_task_lock")
    else:
        pass
