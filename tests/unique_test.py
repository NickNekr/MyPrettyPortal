import pandas as pd

from apps.services.celery_services.duplication.dataframes import (
    get_dataframe_from_parquet,
)

# Данные повторяются в:  Index(['REGION_NAME', 'SPEC_NAME', 'SPEC_CODE', 'USER_ROLE', 'USER_ROLE_ID',
#        'LPU_ID', 'LPU_NAME', 'OGRN', 'MO_ID', 'MO_NAME'],
#       dtype='object')


def unique_test():
    df = get_dataframe_from_parquet()
    duplicated_logins = df.duplicated(subset=["LOGIN"], keep=False)
    differences: pd.DataFrame = df[duplicated_logins].groupby("LOGIN").nunique()

    differences = differences.loc[:, ~differences.eq(1).all()]
    print("Данные повторяются в: ", differences.columns)


if __name__ == "__main__":
    unique_test()
