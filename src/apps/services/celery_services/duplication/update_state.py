from apps.services.celery_services.duplication.dataframes import save_to_parquet
from apps.services.celery_services.duplication.decompostion_data import (
    retrieves_data,
    add_new_data,
    delete_data,
    update_data,
)


def update_database() -> None:
    """
    Executes a sequence of operations to update database.

    Following steps:
    1. Retrieves a dictionary of dataframes and a new dataframe using the 'retrieves_data()'.

    2. Adds new data from the retrieves dataframes using the 'add_new_data()'.

    3. Deletes data from the retrieves dataframes using the 'delete_data()'.

    4. Updates data from the retrieves dataframes using the 'update_data()'.

    5. Saves the new dataframe 'new_df' to Parquet format using the 'save_to_parquet()'.
    """
    dict_dataframes, new_df = retrieves_data()
    add_new_data(dict_dataframes)
    delete_data(dict_dataframes)
    update_data(dict_dataframes)
    save_to_parquet(new_df)
