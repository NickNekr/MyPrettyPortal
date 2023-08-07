import time
import os

from flask import Flask

from apps.orm_db_app.database import db
from config import app_config
from apps.data_routes.data_routes import data_bp
from apps.celery_routes.celery import celery_bp


def create_app() -> Flask:
    """
    Create an :class:`~flask.app.Flask` and register blueprints.
    :return: '~flask.app.Flask' object.
    """
    app = Flask(__name__)

    with app.app_context():
        app.register_blueprint(data_bp, url_prefix="/data")
        app.register_blueprint(celery_bp, url_prefix="/celery")
        app.config.from_object(app_config)

        db.init_app(app)
        # wait for the orm_db_app to load
        if "DOCKER_CONTAINER" in os.environ:
            time.sleep(15)
        return app
