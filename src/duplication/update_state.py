from redis_app.red import redis_client
from duplication.first_duplic import first_duplication
from duplication.dataframes import (
    save_to_parquet,
    get_merged_dataframes,
    add_data,
)


# def delete_data(df):
#     del_users_df = get_user_df(df)
#     delete_users(del_users_df)


def main_update():
    if not redis_client.get("data_in_parquet"):
        first_duplication()
        return
    dataframes = get_merged_dataframes()
    add_data(dataframes["new"])
    save_to_parquet(dataframes["all_data"])
