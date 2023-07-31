import json
import pandas as pd

from config import app_config
from redis_app.red import redis_client
from duplication.models import add_model, get_model_df, ModelsCol, add_lpus
from duplication.users import add_users
from database.models import User, Lpu


def get_data_from_db():
    return pd.DataFrame


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
    result = old_df.merge(new_df, how="outer", indicator=True)
    without_both = result[result["_merge"] != "both"]
    for_del_df = without_both[without_both["_merge"] == "left_only"]
    for_add_df = without_both[without_both["_merge"] != "left_only"]
    result.drop("_merge", axis=1, inplace=True)
    return {
        "add": for_add_df,
        "del": for_del_df,
        "all_data": result,
    }


def add_data(df: pd.DataFrame):
    if df.empty:
        return

    user_frame = get_model_df(df, User)
    add_users(user_frame)

    lpus_frame = get_model_df(df, Lpu)
    add_lpus(lpus_frame)

    change_main_dataframe(df)

    frames = get_frames(df)
    add_frames_to_db(frames)
