from flask import Blueprint, jsonify

from config import app_config

celery_bp = Blueprint("celery", __name__)


@celery_bp.get("/test")
def test_page():
    return jsonify(message="Hello, DIT!"), app_config.ResponseStatusCode.OK


@celery_bp.get("/update")
def update():
    from apps.celery_app.tasks import update_data

    update_data.delay()
    return jsonify(message="Updating..."), app_config.ResponseStatusCode.OK
