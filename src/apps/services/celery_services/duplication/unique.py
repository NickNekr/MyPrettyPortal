import json

from config import app_config


def unique_test(df):
    for unique_data in app_config.UniqueTest.MODELS:
        tmp = (
            df[unique_data["columns"]]
            .groupby(unique_data["unique"], as_index=False)
            .agg(lambda x: set(x))
        )
        tmp.set_index(unique_data["unique"], inplace=True)
        tmp["NOT_UNIQUE"] = tmp.apply(
            lambda row: len(row[unique_data["not_unique_cols"]]) != 1, axis=1
        )
        tmp = tmp[tmp["NOT_UNIQUE"]].drop("NOT_UNIQUE", axis=1)
        if not tmp.empty:
            not_consistent_data = tmp.index.to_frame().to_dict("records")
            not_consistent_data.sort(key=lambda row: row[unique_data["unique"]])
            if (
                not_consistent_data
                != app_config.NOT_CONSISTENT_DATA[unique_data["unique"]]
            ):
                raise Exception(json.dumps(not_consistent_data, indent=4))
