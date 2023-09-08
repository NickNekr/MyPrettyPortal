from celery import Celery

from config import app_config


def create_celery() -> Celery:
    """
    Creates and configures a Celery instance.

    Returns:
        Celery: A configured Celery instance.
    """
    celery_app = Celery("duplication")

    # Configure Celery using the CeleryConfig object from app_config
    celery_app.config_from_object(app_config.CeleryConfig)

    TaskBase = celery_app.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            from wsgi import app

            # Establish an application context before executing the task
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery_app.Task = ContextTask
    return celery_app
