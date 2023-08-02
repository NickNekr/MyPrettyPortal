import time
import os

from flask import Flask

from apps.database_app.database import db
from config import app_config
from apps.data_routes.data_routes import data_bp
from apps.celery_routes.celery import celery_bp


def create_app():
    app = Flask(__name__)

    with app.app_context():
        app.register_blueprint(data_bp, url_prefix="/data")
        app.register_blueprint(celery_bp, url_prefix="/celery")
        app.config.from_object(app_config)

        db.init_app(app)
        # db.create_all()
        # wait for the database_app to load
        if "DOCKER_CONTAINER" in os.environ:
            time.sleep(15)
        return app
