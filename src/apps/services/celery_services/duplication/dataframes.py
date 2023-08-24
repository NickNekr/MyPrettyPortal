import json
from functools import reduce
import pandas as pd

from config import app_config
from apps.services.redis_services.red import redis_client
from apps.services.celery_services.duplication.models import (
    add_model,
    del_model,
    add_lpus,
    MergeDataColumns,
    UpdateModels,
    update_model,
    DeleteModels,
    add_users,
)
from apps.services.orm_db_services.models import (
    Lpu,
    AdditionalInfo,
    UsersSpec,
    UsersRole,
    User,
    UsersLpu,
)
from apps.services.oracle_db_services.oracle_db import oracle_client
from apps.services.orm_db_services.database import db

# Index(['LOGIN_ID', 'LOGIN', 'LAST_NAME', 'FIRST_NAME', 'SECOND_NAME', 'SNILS', 'REGION_NAME',
#        'PHONE', 'EMAIL', 'SPEC_NAME', 'SPEC_CODE', 'USER_ROLE', 'USER_ROLE_ID',
#        'LPU_ID', 'LPU_NAME', 'OGRN', 'MO_ID', 'MO_NAME'],
#       dtype='object')


def get_data_from_db() -> pd.DataFrame:
    """
    Executes a gold query, fetches the data, and converts it to a DataFrame.
    :return: extracted data as a DataFrame
    """
    df = pd.read_sql(app_config.DataBase.GOLD_QUERY, con=oracle_client.conn)
    df.columns = df.columns.str.upper()
    return df


def get_dataframe_from_parquet() -> pd.DataFrame:
    """
    Reads data from a parquet file and stores it in a data frame.
    :return: extracted data
    """
    return pd.read_parquet(app_config.PARQUET_PATH)


def save_to_parquet(dataframe: pd.DataFrame) -> None:
    """
    Saves the dataframe to a parquet file and sets the 'data_in_parquet' boolean variable in Redis to True
    :param dataframe: extracted data
    """
    dataframe.to_parquet(app_config.PARQUET_PATH, compression="gzip")
    redis_client.conn.set("data_in_parquet", "true")


def get_dataframe_from_file() -> pd.DataFrame:
    """
    Reads data from a excel file and stores it in a data frame.
    :return: extracted data
    """
    return pd.read_excel(app_config.EXCEL_FILE_PATH)


def get_df() -> pd.DataFrame:
    """
    Reads data from an Oracle file or database, depending on the env.
    :return: extracted data
    """
    if app_config.ENV == "development":
        df = get_dataframe_from_file()
    else:
        df = get_data_from_db()
    return df.astype("str").fillna("None")


def add_frames_to_db(frames: dict[db.Model, dict[str, pd.DataFrame]]) -> None:
    """
    For each model in frames add data to database.
    :param frames: dict of model and dataframes.
    """
    for model in frames:
        add_model(frames[model]["new"], model)


def del_frames_from_db(frames: dict[db.Model, dict[str, pd.DataFrame]]) -> None:
    """
    For each model in frames delete data from database.
    :param frames: dict of model and dataframes.
    """
    for model in DeleteModels.MODELS:
        del_model(frames[model]["del"], model)


def update_frames_from_db(frames: dict[db.Model, dict[str, pd.DataFrame]]) -> None:
    """
    For each model in frames update data in database.
    :param frames: dict of model and dataframes.
    """
    for model in UpdateModels.MODELS:
        update_model(frames[model]["update"], model)


def add_user_id_to_dataframes(frames: dict[db.Model, dict[str, pd.DataFrame]]) -> None:
    """
    Adds column 'USER_ID' to 'new' and 'del' dataframes with column 'LOGIN'.
    :param frames: dict of model and dataframes.
    """
    login_to_id = json.loads(redis_client.conn.get("login_to_id"))
    for model in [AdditionalInfo, UsersSpec, UsersRole, UsersLpu, User]:
        if not frames[model]["new"].empty:
            frames[model]["new"]["USER_ID"] = frames[model]["new"].apply(
                lambda row: login_to_id[row["LOGIN"]], axis=1
            )
        if not frames[model]["del"].empty:
            frames[model]["del"]["USER_ID"] = frames[model]["del"].apply(
                lambda row: login_to_id[row["LOGIN"]], axis=1
            )


def get_update_data(by_model: pd.DataFrame, model: db.Model) -> pd.DataFrame:
    """
    Retrieves data that needs to be updated in the database.
    Data needs to be in left and right dataframes (_merge == "both") and not 'on' columns should be different.
    Also set not 'on' columns right dataframes values.
    :param by_model: merged dataframe on columns depending on model
    :param model: model of database
    :return: extracted data
    """
    if len(MergeDataColumns.MODELS[model]["not_unique_cols"]) == 0:
        return pd.DataFrame(columns=by_model.columns)
    main_condition = by_model["_merge"] == "both"
    conditions = []
    for i in range(len(MergeDataColumns.MODELS[model]["not_unique_cols"])):
        conditions.append(
            by_model[MergeDataColumns.MODELS[model]["not_unique_cols"][i] + "_x"]
            != by_model[MergeDataColumns.MODELS[model]["not_unique_cols"][i] + "_y"]
        )

    condition = reduce(lambda acc, item: acc | item, conditions) & main_condition
    updated_data = by_model[condition].copy()
    for i in range(len(MergeDataColumns.MODELS[model]["not_unique_cols"])):
        updated_data[
            MergeDataColumns.MODELS[model]["not_unique_cols"][i]
        ] = updated_data[MergeDataColumns.MODELS[model]["not_unique_cols"][i] + "_y"]
    updated_data.drop_duplicates(
        subset=MergeDataColumns.MODELS[model]["columns"], inplace=True
    )
    return updated_data


def get_del_data(by_model: pd.DataFrame, model: db.Model) -> pd.DataFrame:
    """
    Retrieves data that needs to be deleted from the database.
    Data needs to be only in left dataframe (_merge == "left_only").
    Also set not 'on' columns left dataframes values.
    :param by_model: merged dataframe on columns depending on model
    :param model: model of database
    :return: extracted data
    """
    del_data = by_model[by_model["_merge"] == "left_only"].copy()
    for i in range(len(MergeDataColumns.MODELS[model]["not_unique_cols"])):
        del_data[MergeDataColumns.MODELS[model]["not_unique_cols"][i]] = del_data[
            MergeDataColumns.MODELS[model]["not_unique_cols"][i] + "_x"
        ]
    del_data.drop_duplicates(
        subset=MergeDataColumns.MODELS[model]["columns"], inplace=True
    )
    return del_data


def get_new_data(by_model: pd.DataFrame, model: db.Model) -> pd.DataFrame:
    """
    Retrieves data that needs to be added in the database.
    Data needs to be only in right dataframe (_merge == "right_only").
    Also set not 'on' columns right dataframes values.
    :param by_model: merged dataframe on columns depending on model
    :param model: model of database
    :return: extracted data
    """
    new_data = by_model[by_model["_merge"] == "right_only"].copy()
    for i in range(len(MergeDataColumns.MODELS[model]["not_unique_cols"])):
        new_data[MergeDataColumns.MODELS[model]["not_unique_cols"][i]] = new_data[
            MergeDataColumns.MODELS[model]["not_unique_cols"][i] + "_y"
        ]

    new_data.drop_duplicates(subset=MergeDataColumns.MODELS[model]["on"], inplace=True)
    return new_data


def retrieves_data(
    data_in_parquet=True,
) -> tuple[dict[db.Model, dict[str, pd.DataFrame]], pd.DataFrame]:
    """
    Fetches data from parquet and database/excel, merges it by each model and retrieves data that needs to be added/deleted/updated in the database.
    If 'data_in_parquet' set to
        - False: than old dataframe init like empty
        - True: than data fetches from parquet
    :param data_in_parquet: boolean values
    :return: retrieves data and new dataframe
    """
    new_df = get_df()
    old_df = (
        get_dataframe_from_parquet()
        if data_in_parquet
        else pd.DataFrame(columns=new_df.columns)
    )

    all_data = {}

    for model in MergeDataColumns.MODELS:
        by_model = (
            old_df[MergeDataColumns.MODELS[model]["columns"]]
            .drop_duplicates(subset=MergeDataColumns.MODELS[model]["columns"])
            .merge(
                new_df[MergeDataColumns.MODELS[model]["columns"]].drop_duplicates(
                    subset=MergeDataColumns.MODELS[model]["columns"]
                ),
                on=MergeDataColumns.MODELS[model]["on"],
                how="outer",
                indicator=True,
            )
        )

        new_data = get_new_data(by_model, model)

        updated_data = get_update_data(by_model, model)

        deleted_data = get_del_data(by_model, model)

        all_data[model] = {"new": new_data, "update": updated_data, "del": deleted_data}

    return all_data, new_df


def add_new_data(frames: dict[db.Model, dict[str, pd.DataFrame]]) -> None:
    """
    Adds data to the database.
    Some models depend on "LOGIN_ID" and "LPU_ID", so we need to add "User" and "LPU" first.
    :param frames: fetched data to add
    """
    add_users(frames[User]["new"])

    add_user_id_to_dataframes(frames)

    add_lpus(frames[Lpu]["new"])

    add_frames_to_db(frames)


def delete_data(frames: dict[db.Model, dict[str, pd.DataFrame]]) -> None:
    """
    Deletes data from the database.
    :param frames: fetched data to delete
    """
    del_frames_from_db(frames)


def update_data(frames: dict[db.Model, dict[str, pd.DataFrame]]) -> None:
    """
    Updates data in the database.
    :param frames: fetched data to update
    """
    update_frames_from_db(frames)
