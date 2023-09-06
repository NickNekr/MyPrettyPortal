import pandas as pd


# Данные повторяются в:  Index(['REGION_NAME', 'SPEC_NAME', 'SPEC_CODE', 'USER_ROLE', 'USER_ROLE_ID',
#        'LPU_ID', 'LPU_NAME', 'OGRN', 'MO_ID', 'MO_NAME'],
#       dtype='object')

PARQUET_PATH = "./Data/supp_raw.parquet"
EXCEL_PATH = ".Data/supp_raw.xlsx"


class MergeDataColumns:
    MODELS = [
        {
            "columns": ["SPEC_CODE", "SPEC_NAME"],
            "unique": "SPEC_CODE",
            "not_unique_cols": "SPEC_NAME",
        },
        {
            "columns": ["USER_ROLE_ID", "USER_ROLE"],
            "unique": "USER_ROLE_ID",
            "not_unique_cols": "USER_ROLE",
        },
        {
            "columns": ["LPU_ID", "LPU_NAME"],
            "unique": "LPU_ID",
            "not_unique_cols": "LPU_NAME",
        },
        {
            "columns": ["MO_ID", "MO_NAME"],
            "unique": "MO_ID",
            "not_unique_cols": "MO_NAME",
        },
    ]


def unique_test():
    pd.set_option("display.max_columns", None)
    pd.set_option("display.max_colwidth", None)
    # df = pd.read_excel("./Data/supp_raw.xlsx")
    # df.to_parquet("./Data/supp_raw.parquet")
    df = pd.read_parquet(PARQUET_PATH)
    print(df[df["LOGIN"] == "VRadevich"])
    for model in MergeDataColumns.MODELS:
        tmp = (
            df[model["columns"]]
            .groupby(model["unique"], as_index=False)
            .agg(lambda x: set(x))
        )
        tmp["NOT_UNIQUE"] = tmp.apply(
            lambda row: len(row[model["not_unique_cols"]]) != 1, axis=1
        )
        print(tmp[tmp["NOT_UNIQUE"]].drop("NOT_UNIQUE", axis=1))


if __name__ == "__main__":
    unique_test()
