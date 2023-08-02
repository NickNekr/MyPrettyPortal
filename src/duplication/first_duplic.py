from redis_app.red import redis_client
from duplication.dataframes import (
    get_df,
    save_to_parquet,
    add_new_data,
)


# Index(['LOGIN_ID', 'LOGIN', 'LAST_NAME', 'FIRST_NAME', 'SECOND_NAME', 'SNILS', 'REGION_NAME',
#        'PHONE', 'EMAIL', 'SPEC_NAME', 'SPEC_CODE', 'USER_ROLE', 'USER_ROLE_ID',
#        'LPU_ID', 'LPU_NAME', 'OGRN', 'MO_ID', 'MO_NAME'],
#       dtype='object')


def init_redis_var():
    redis_client.set("data_in_parquet", "true")
    redis_client.set("login_to_id", "{}")


def first_duplication():
    df = get_df()
    save_to_parquet(df)
    init_redis_var()
    add_new_data(df)
