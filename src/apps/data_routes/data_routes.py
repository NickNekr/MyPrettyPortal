from flask import Blueprint, request, jsonify

from config import app_config
from apps.orm_db_app.database import db
from apps.orm_db_app.models import User, LpusMo

data_bp = Blueprint("data", __name__)


@data_bp.get("/test")
def test_page():
    return jsonify(message="Hello, DIT!"), app_config.ResponseStatusCode.OK


@data_bp.post("/")
def add_user():
    data = request.get_json()
    user = User(data)
    db.session.add(user)
    db.session.commit()
    return (
        jsonify(message="User added!", user_id=user.id),
        app_config.ResponseStatusCode.OK,
    )


@data_bp.get("/filial/<int:lpu_id>")
def get_filial(lpu_id):
    filials = [lpu.lpu_id for lpu in LpusMo.query.filter(LpusMo.mo_id == lpu_id)]
    return (
        jsonify(message=f"Filials of {lpu_id}!", filleals=filials),
        app_config.ResponseStatusCode.OK,
    )


@data_bp.delete("/<int:user_id>")
def delete_user(user_id):
    user = User.query.filter(User.id == user_id).first()

    if user is None:
        return (
            jsonify(message="User not founded!"),
            app_config.ResponseStatusCode.NOT_FOUND,
        )

    db.session.delete(user)
    db.session.commit()

    return jsonify(message="User deleted!"), app_config.ResponseStatusCode.OK


@data_bp.get("/<int:user_id>")
def check_user(user_id):
    user = User.query.filter(User.id == user_id).first()

    if user is None:
        return (
            jsonify(message="User not founded!"),
            app_config.ResponseStatusCode.NOT_FOUND,
        )

    user_dict = {
        "LAST_NAME": user.last_name,
        "FIRST_NAME": user.first_name,
        "SECOND_NAME": user.second_name,
        "SNILS": user.snils,
        "LOGIN": user.login,
    }

    return (
        jsonify(message="User founded!", user=user_dict),
        app_config.ResponseStatusCode.OK,
    )
