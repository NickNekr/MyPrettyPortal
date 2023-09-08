import json
from flask_sqlalchemy.model import Model
import pandas as pd

from config import app_config
from apps.services.redis_services.red import redis_client
from apps.services.celery_services.duplication.models import add_model
from apps.services.orm_db_services.models import (
    AdditionalInfo,
    UsersSpec,
    UsersRole,
    User,
    UsersLpu,
)
from apps.services.oracle_db_services.oracle_db import oracle_client
from apps.services.celery_services.duplication.unique import unique_test

# Index(['LOGIN_ID', 'LOGIN', 'LAST_NAME', 'FIRST_NAME', 'SECOND_NAME', 'SNILS', 'REGION_NAME',
#        'PHONE', 'EMAIL', 'SPEC_NAME', 'SPEC_CODE', 'USER_ROLE', 'USER_ROLE_ID',
#        'LPU_ID', 'LPU_NAME', 'OGRN', 'MO_ID', 'MO_NAME'],
#       dtype='object')


def get_data_from_db() -> pd.DataFrame:
    """
    Executes a gold query, fetches the data, and converts it to a DataFrame.
    :return: extracted data as a DataFrame
    """
    df = pd.read_sql(
        app_config.DataBase.GOLD_QUERY, con=oracle_client.conn  # pyright: ignore
    )
    df.columns = df.columns.str.upper()
    return df


def get_dataframe_from_parquet() -> pd.DataFrame:
    """
    Reads data from a parquet file and stores it in a data frame.
    :return: extracted data
    """
    return pd.read_parquet(app_config.PARQUET_PATH)  # pyright: ignore


def save_to_parquet(dataframe: pd.DataFrame) -> None:
    """
    Saves the dataframe to a parquet file and sets the 'data_in_parquet' boolean variable in Redis to True
    :param dataframe: extracted data
    """
    dataframe.to_parquet(app_config.PARQUET_PATH, compression="gzip")  # pyright: ignore
    redis_client.conn.set("data_in_parquet", "true")


def get_dataframe_from_file() -> pd.DataFrame:
    """
    Reads data from a excel file and stores it in a data frame.
    :return: extracted data
    """
    return pd.read_excel(app_config.EXCEL_FILE_PATH)  # pyright: ignore


def tmp_crutch(frame: pd.DataFrame) -> None:
    for row in app_config.CONSISTENT_DATA:
        frame.loc[frame[row.id_name] == row.id, row.value_name] = row.value


def get_df() -> pd.DataFrame:
    """
    Reads data from an Oracle file or database, depending on the env.
    :return: extracted data
    """
    if app_config.ENV == "development":
        df = get_dataframe_from_file()
    else:
        df = get_data_from_db()
    unique_test(df)
    tmp_crutch(df)
    return df.astype("str").fillna("None")


def add_frames_to_db(frames: dict[Model, dict[str, pd.DataFrame]]) -> None:
    """
    For each model in frames add data to database.
    :param frames: dict of model and dataframes.
    """
    for model in frames:
        add_model(frames[model]["new"], model)


def add_user_id_to_dataframes(frames: dict[Model, dict[str, pd.DataFrame]]) -> None:
    """
    Adds column 'USER_ID' to 'new' and 'del' dataframes with column 'LOGIN'.
    :param frames: dict of model and dataframes.
    """
    login_to_id = json.loads(redis_client.conn.get("login_to_id"))  # pyright: ignore
    for model in [AdditionalInfo, UsersSpec, UsersRole, UsersLpu, User]:
        if not frames[model]["new"].empty:
            frames[model]["new"]["USER_ID"] = frames[model]["new"].apply(
                lambda row: login_to_id[row["LOGIN"]], axis=1
            )
        if not frames[model]["del"].empty:
            frames[model]["del"]["USER_ID"] = frames[model]["del"].apply(
                lambda row: login_to_id[row["LOGIN"]], axis=1
            )
