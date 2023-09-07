import json
from functools import reduce
from flask_sqlalchemy.model import Model
import pandas as pd

from wsgi import app
from apps.services.redis_services.red import redis_client
from apps.services.orm_db_services.database import db
from apps.services.orm_db_services.models import (
    User,
    AdditionalInfo,
    Role,
    Specialities,
    Lpu,
    LpusMo,
    UsersRole,
    UsersSpec,
    UsersLpu,
)


class MergeDataColumns:
    MODELS: dict[Model, dict] = {
        Specialities: {
            "columns": ["SPEC_CODE", "SPEC_NAME"],
            "on": ["SPEC_CODE"],
            "not_unique_cols": ["SPEC_NAME"],
        },
        Role: {
            "columns": ["USER_ROLE_ID", "USER_ROLE"],
            "on": ["USER_ROLE_ID"],
            "not_unique_cols": ["USER_ROLE"],
        },
        Lpu: {
            "columns": ["LPU_ID", "LPU_NAME", "OGRN", "MO_ID", "MO_NAME"],
            "on": ["LPU_ID", "MO_ID"],
            "not_unique_cols": ["MO_NAME", "OGRN", "LPU_NAME"],
        },
        User: {
            "columns": ["LOGIN", "LAST_NAME", "FIRST_NAME", "SECOND_NAME", "SNILS"],
            "on": ["LOGIN"],
            "not_unique_cols": ["LAST_NAME", "FIRST_NAME", "SECOND_NAME", "SNILS"],
        },
        AdditionalInfo: {
            "columns": ["LOGIN", "PHONE", "EMAIL", "REGION_NAME"],
            "on": ["LOGIN", "PHONE", "EMAIL", "REGION_NAME"],
            "not_unique_cols": [],
        },
        UsersSpec: {
            "columns": ["LOGIN", "SPEC_CODE"],
            "on": ["LOGIN", "SPEC_CODE"],
            "not_unique_cols": [],
        },
        UsersRole: {
            "columns": ["USER_ROLE_ID", "LOGIN"],
            "on": ["USER_ROLE_ID", "LOGIN"],
            "not_unique_cols": [],
        },
        LpusMo: {
            "columns": ["LPU_ID", "MO_ID"],
            "on": ["LPU_ID", "MO_ID"],
            "not_unique_cols": [],
        },
        UsersLpu: {
            "columns": ["LOGIN", "LPU_ID"],
            "on": ["LOGIN", "LPU_ID"],
            "not_unique_cols": [],
        },
    }


class UpdateModels:
    MODELS = {
        User: {"field": User.login, "col": "LOGIN"},
        Specialities: {"field": Specialities.spec_code, "col": "SPEC_CODE"},
        Role: {"field": Role.role_id, "col": "USER_ROLE_ID"},
        Lpu: {"field": Lpu.id, "col": "LPU_ID"},
    }


class DeleteModels:
    MODELS = {
        User: [(User.login, "LOGIN")],
        Specialities: [(Specialities.spec_code, "SPEC_CODE")],
        Role: [(Role.role_id, "USER_ROLE_ID")],
        Lpu: [(Lpu.id, "LPU_ID")],
        UsersSpec: [(UsersSpec.users_id, "USER_ID"), (UsersSpec.spec_id, "SPEC_CODE")],
        UsersRole: [
            (UsersRole.users_id, "USER_ID"),
            (UsersRole.role_id, "USER_ROLE_ID"),
        ],
        UsersLpu: [(UsersLpu.users_id, "USER_ID"), (UsersLpu.lpu_id, "LPU_ID")],
        LpusMo: [(LpusMo.lpu_id, "LPU_ID"), (LpusMo.mo_id, "MO_ID")],
        AdditionalInfo: [
            (AdditionalInfo.user_id, "USER_ID"),
            (AdditionalInfo.email, "EMAIL"),
            (AdditionalInfo.phone, "PHONE"),
            (AdditionalInfo.region, "REGION_NAME"),
        ],
    }


def add_lpus(frame: pd.DataFrame) -> None:
    """
    Creates list of '~apps.database_app.models.Lpu', adds it to database and save set of lpu_id in redis.
    :param frame: Lpus's frame
    """
    if frame.empty:
        return

    lpus = []
    added_lpus = redis_client.conn.smembers("lpus_ids")
    frame.apply(
        lambda x: (lpus.append(Lpu(x)), added_lpus.add(x["LPU_ID"]))
        if x["LPU_ID"] not in added_lpus
        else None,
        axis=1,
    )

    frame.drop(columns=["LPU_ID", "LPU_NAME", "OGRN"], inplace=True)
    frame.apply(
        lambda x: (lpus.append(Lpu(x)), added_lpus.add(x["MO_ID"]))
        if x["MO_ID"] not in added_lpus
        else None,
        axis=1,
    )

    with app.app_context():
        db.session.add_all(lpus)
        db.session.commit()

    redis_client.conn.sadd("lpus_ids", *added_lpus)


def add_users(frame: pd.DataFrame) -> None:
    """
    Creates list of '~apps.database_app.models.User', adds it to database and save dict 'login_to_id' in redis.
    :param frame: User's dataframe
    """
    if frame.empty:
        return

    users = []
    json_lti_str: str | None = redis_client.conn.get("login_to_id")

    if json_lti_str is None:
        return

    json_lti = json.loads(json_lti_str)

    frame.apply(
        lambda x: users.append(User(x)) if x["LOGIN"] not in json_lti else None, axis=1
    )

    with app.app_context():
        db.session.add_all(users)
        db.session.commit()

        for user in users:
            json_lti[user.login] = user.id
    json_lti = json.dumps(json_lti)

    redis_client.conn.set("login_to_id", json_lti)


def add_model(frame: pd.DataFrame, model: db.Model) -> None:  # type: ignore
    """
    Creates list of '~apps.database_app.database.db.Model' and adds it to database.
    If model is User or Lpu, then does nothing.
    :param frame: model's dataframe
    :param model: model of database
    """
    if frame.empty or model == User or model == Lpu:
        return

    models = []
    frame.apply(lambda x: models.append(model(x)), axis=1)

    with app.app_context():
        db.session.add_all(models)
        db.session.commit()


def del_model(frame: pd.DataFrame, model: db.Model) -> None:  # type: ignore
    """
    Delete objects from database.
    :param frame: model's dataframe
    :param model: model of database
    """
    if frame.empty:
        return
    with app.app_context():
        frame.apply(
            lambda row: model.query.filter(
                reduce(
                    lambda acc, item: acc & item,
                    [pair[0] == row[pair[1]] for pair in DeleteModels.MODELS[model]],
                )
            ).delete(),
            axis=1,
        )
        db.session.commit()
    if model == User:
        delete_users_id_from_redis(frame)
    if model == Lpu:
        delete_lpus_id_from_redis(frame)


def delete_users_id_from_redis(frame: pd.DataFrame) -> None:
    """
    Remove logins from the redis "login_to_id" variable that have been removed from the database.
    :param frame: user's frame
    """
    if frame.empty:
        return

    lti_str = redis_client.conn.get("login_to_id")

    if lti_str is None:
        return

    login_to_id: dict = json.loads(lti_str)
    frame.apply(lambda row: login_to_id.pop(row["LOGIN"]), axis=1)
    json_lti = json.dumps(login_to_id)
    redis_client.conn.set("login_to_id", json_lti)


def delete_lpus_id_from_redis(frame: pd.DataFrame) -> None:
    """
    Remove lpu's id from the redis "lpus_id" variable that have been removed from the database.
    :param frame: lpus's frame
    """
    if frame.empty:
        return
    redis_client.conn.srem("lpus_id", *frame["LPU_ID"])


def update_model(frame: pd.DataFrame, model: db.Model) -> None:  # type: ignore
    """
    Update objects in database.
    :param frame: model's dataframe
    :param model: model of database
    """
    with app.app_context():
        frame.apply(
            lambda x: model.query.filter(
                UpdateModels.MODELS[model]["field"]
                == x[UpdateModels.MODELS[model]["col"]]
            ).update(
                {
                    col.lower(): x[col]
                    for col in MergeDataColumns.MODELS[model]["not_unique_cols"]
                }
            ),
            axis=1,
        )
        db.session.commit()
