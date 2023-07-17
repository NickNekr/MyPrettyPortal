import logging
import traceback

from .celery import celery_app
from redis_app.red import redis_client
from duplication.update_state import main_update


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
            main_update()
        except Exception:
            logging.error(traceback.format_exc())
        finally:
            redis_client.delete("update_task_lock")
    else:
        pass
