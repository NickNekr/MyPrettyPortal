import json
import pandas as pd

from config import app_config
from apps.redis_app.red import redis_client
from apps.celery_app.duplication.models import (
    add_model,
    get_model_df,
    ModelsCol,
    add_lpus,
)
from apps.celery_app.duplication.users import add_users
from apps.database_app.models import User, Lpu
from apps.database_app.database import db


def get_data_from_db() -> pd.DataFrame:
    """
    Executes a gold query, fetches the data, and converts it to a DataFrame.
    :return: extracted data
    """
    with db.conn.cursor() as cursor:
        cursor.execute(app_config.GOLD_QUERY)
        column_names = [columns_desc[0] for columns_desc in cursor.description]
        data = cursor.fetchall()
    return pd.DataFrame(data, columns=column_names)


def get_dataframe_from_parquet():
    df = pd.read_parquet(app_config.PARQUET_PATH)
    return df.astype("str")


def save_to_parquet(dataframe):
    dataframe.to_parquet(app_config.PARQUET_PATH, compression="gzip")


def get_dataframe_from_file():
    dataframe: pd.DataFrame = pd.read_excel(
        app_config.EXCEL_FILE_PATH,
        dtype=str,
    )
    return dataframe


def get_df():
    if app_config.ENV == "development":
        df = get_dataframe_from_file()
    else:
        df = get_data_from_db()
    return df.fillna("None")


def add_frames_to_db(frames):
    for model in frames:
        add_model(frames[model], model)


def get_frames(df):
    return {
        model: get_model_df(df, model)
        for model in ModelsCol.MODELS
        if model != User and model != Lpu
    }


def change_main_dataframe(frame: pd.DataFrame):
    login_to_id = json.loads(redis_client.get("login_to_id"))

    frame["USER_ID"] = frame.apply(lambda row: login_to_id[row["LOGIN"]], axis=1)


def get_merged_dataframes():
    old_df = get_dataframe_from_parquet()
    new_df = get_df()

    login_to_id: dict = json.loads(redis_client.get("login_to_id"))

    result = old_df.merge(new_df, how="outer", indicator=True)
    result.drop(columns="both", inplace=True)
    left_only_predicate_df = result["_merge"] == "left_only"
    left_only = result[left_only_predicate_df]
    right_only = result[~left_only_predicate_df]
    in_saved_login_predicate_df = right_only["LOGIN"].isin(login_to_id)
    new_data_df = right_only[~in_saved_login_predicate_df]
    changed_data_df = right_only[in_saved_login_predicate_df]
    return {
        "new": new_data_df,
        "changed": changed_data_df,
        "all": new_df,
        "del": left_only,
    }


def add_new_data(df: pd.DataFrame):
    if df.empty:
        return

    user_frame = get_model_df(df, User)
    add_users(user_frame)

    lpus_frame = get_model_df(df, Lpu)
    add_lpus(lpus_frame)

    change_main_dataframe(df)

    frames = get_frames(df)
    add_frames_to_db(frames)
