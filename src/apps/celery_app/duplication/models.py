import re
import pandas as pd

from wsgi import app
from apps.celery_app.duplication.users import add_users
from apps.redis_app.red import redis_client
from apps.database_app import db
from apps.database_app import User, AdditionalInfo, Role, Specialities, Lpu, LpusMo


class ModelsCol:
    MODELS = {
        User: {
            "col": ["LOGIN", "SNILS", "LAST_NAME", "FIRST_NAME", "SECOND_NAME"],
            "sub": ["LOGIN"],
        },
        AdditionalInfo: {
            "col": ["LOGIN", "REGION_NAME", "PHONE", "EMAIL", "USER_ID"],
            "sub": ["LOGIN", "REGION_NAME"],
        },
        Role: {
            "col": ["USER_ROLE_ID", "USER_ROLE"],
            "sub": ["USER_ROLE_ID", "USER_ROLE"],
        },
        Specialities: {
            "col": [
                "SPEC_CODE",
                "SPEC_NAME",
            ],
            "sub": ["SPEC_CODE", "SPEC_NAME"],
        },
        Lpu: {
            "col": ["LPU_ID", "LPU_NAME", "OGRN", "MO_ID", "MO_NAME"],
            "sub": ["LPU_ID", "MO_ID"],
        },
        LpusMo: {
            "col": ["LPU_ID", "MO_ID"],
            "sub": ["LPU_ID", "MO_ID"],
        },
    }


def add_lpus(frame: pd.DataFrame):
    if frame.empty:
        return

    lpus = []
    added_lpus = redis_client.smembers("lpus_ids")
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

    redis_client.sadd("lpus_ids", *added_lpus)


def add_model(frame: pd.DataFrame, model: db.Model):
    if frame.empty:
        return

    if model == User:
        add_users(frame)
        return

    if model == Lpu:
        add_lpus(frame)
        return

    models = []
    frame.apply(lambda x: models.append(model(x)), axis=1)

    with app.app_context():
        db.session.add_all(models)
        db.session.commit()


def get_model_df(df: pd.DataFrame, model: db.Model):
    frame = df.loc[:, ModelsCol.MODELS[model]["col"]]
    frame.drop_duplicates(subset=ModelsCol.MODELS[model]["sub"], inplace=True)

    if model == User:
        df["SNILS"] = df["SNILS"].apply(lambda x: "".join(re.findall(r"\d+", x)))

    return frame
