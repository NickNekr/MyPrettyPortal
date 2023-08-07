import json
import pandas as pd

from wsgi import app
from apps.redis_app.red import redis_client
from apps.orm_db_app.models import User
from apps.orm_db_app.database import db


def delete_users(user_frame: pd.DataFrame):
    if user_frame.empty:
        return

    with app.app_context():
        user_frame.apply(
            lambda x: User.query.filter(User.login == x["LOGIN"]).delete(),
            axis=1,
        )
        db.session.commit()


def add_users(frame: pd.DataFrame):
    if frame.empty:
        return

    users = []
    json_lti = json.loads(redis_client.get("login_to_id"))

    frame.apply(
        lambda x: users.append(User(x)) if x["LOGIN"] not in json_lti else None, axis=1
    )

    with app.app_context():
        db.session.add_all(users)
        db.session.commit()

        for user in users:
            json_lti[user.login] = user.id
    json_lti = json.dumps(json_lti)

    redis_client.set("login_to_id", json_lti)
