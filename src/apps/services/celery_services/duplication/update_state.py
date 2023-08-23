from apps.services.redis_services.red import redis_client
from apps.services.celery_services.duplication.dataframes import (
    save_to_parquet,
    retrieves_data,
    add_new_data,
    delete_data,
    update_data,
)


def init_redis_var() -> bool:
    """
    Sets redis variables in the first update.
    :return always False to explain, that data_in_parquet doesn't set to True
    """
    redis_client.conn.set("login_to_id", "{}")
    redis_client.conn.delete("lpus_ids")
    return False


def update_database() -> None:
    """
    Executes a sequence of operations to update database.

    Following steps:
    1. Checks if the 'data_in_parquet' key exists in the Redis database.
       - If the key exists, sets 'first_dup' to True, indicating that data already exists in Parquet.
       - If the key does not exist, initializes the Redis variables using the 'init_redis_var()' and sets 'first_dup' to False.

    2. Retrieves a dictionary of dataframes and a new dataframe using the 'retrieves_data()'.

    3. Adds new data from the retrieves dataframes using the 'add_new_data()'.

    4. Deletes data from the retrieves dataframes using the 'delete_data()'.

    5. Updates data from the retrieves dataframes using the 'update_data()'.

    6. Saves the new dataframe 'new_df' to Parquet format using the 'save_to_parquet()'.
    """
    first_dup = True if redis_client.conn.get("data_in_parquet") else init_redis_var()
    dict_dataframes, new_df = retrieves_data(first_dup)
    add_new_data(dict_dataframes)
    delete_data(dict_dataframes)
    update_data(dict_dataframes)
    save_to_parquet(new_df)
