from apps.redis_app.red import redis_client
from apps.celery_app.duplication.dataframes import (
    save_to_parquet,
    get_merged_dataframes,
    add_new_data,
    delete_data,
    update_data,
)


def init_redis_var():
    redis_client.set("login_to_id", "{}")
    redis_client.delete("lpus_ids")
    return False


def update_database() -> None:
    """
    :return:
    """
    first_dup = True if redis_client.get("data_in_parquet") else init_redis_var()
    dict_dataframes, new_df = get_merged_dataframes(first_dup)
    add_new_data(dict_dataframes)
    delete_data(dict_dataframes)
    update_data(dict_dataframes)
    save_to_parquet(new_df)


update_database()
