from sqlalchemy import create_engine

from config import app_config


class DataBase(object):
    def __init__(self):
        connection_string = f"oracle+cx_oracle://{app_config.DataBase.USER}:{app_config.DataBase.PASSWORD}@{app_config.DataBase.HOST}:{app_config.DataBase.PORT}/{app_config.DataBase.SID}"
        self.conn = create_engine(connection_string)

    def __del__(self):
        self.conn.dispose()


oracle_client = DataBase() if app_config.ENV == "production" else None
