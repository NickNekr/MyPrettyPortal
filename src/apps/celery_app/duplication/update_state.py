from apps.redis_app.red import redis_client
from apps.celery_app.duplication.first_duplic import first_duplication
from apps.celery_app.duplication.dataframes import (
    save_to_parquet,
    get_merged_dataframes,
    add_new_data,
)


# def delete_data(df):
#     del_users_df = get_user_df(df)
#     delete_users(del_users_df)


def main_update():
    if not redis_client.get("data_in_parquet"):
        first_duplication()
        return
    dataframes = get_merged_dataframes()
    add_new_data(dataframes["new"])
    save_to_parquet(dataframes["all_data"])
