from functools import reduce
from flask_sqlalchemy.model import Model
import pandas as pd

from apps.services.redis_services.red import redis_client
from apps.services.celery_services.duplication.models import (
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
    User,
)
from apps.services.celery_services.duplication.dataframes import (
    get_df,
    get_dataframe_from_parquet,
    add_user_id_to_dataframes,
    add_frames_to_db,
)


def get_update_data(by_model: pd.DataFrame, model: Model) -> pd.DataFrame:
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


def get_del_data(by_model: pd.DataFrame, model: Model) -> pd.DataFrame:
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


def get_new_data(by_model: pd.DataFrame, model: Model) -> pd.DataFrame:
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


def init_redis_var() -> None:
    """
    Sets redis variables in the first update.
    """
    redis_client.conn.set("login_to_id", "{}")
    redis_client.conn.delete("lpus_ids")


def retrieves_data() -> tuple[dict[Model, dict[str, pd.DataFrame]], pd.DataFrame]:
    """
    Fetches data from parquet and database/excel, merges it by each model and retrieves data that needs to be added/deleted/updated in the database.
    If 'data_in_parquet' set to
        - False: than old dataframe init like empty
        - True: than data fetches from parquet
    :return: retrieves data and new dataframe
    """
    data_in_parquet = (
        True if redis_client.conn.get("data_in_parquet") else init_redis_var()
    )

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


def add_new_data(frames: dict[Model, dict[str, pd.DataFrame]]) -> None:
    """
    Adds data to the database.
    Some models depend on "LOGIN_ID" and "LPU_ID", so we need to add "User" and "LPU" first.
    :param frames: fetched data to add
    """
    add_users(frames[User]["new"])

    add_user_id_to_dataframes(frames)

    add_lpus(frames[Lpu]["new"])

    add_frames_to_db(frames)


def delete_data(frames: dict[Model, dict[str, pd.DataFrame]]) -> None:
    """
    For each model in frames delete data from database.
    :param frames: dict of model and dataframes.
    """
    for model in DeleteModels.MODELS:
        del_model(frames[model]["del"], model)


def update_data(frames: dict[Model, dict[str, pd.DataFrame]]) -> None:
    """
    For each model in frames update data in database.
    :param frames: dict of model and dataframes.
    """
    for model in UpdateModels.MODELS:
        update_model(frames[model]["update"], model)
