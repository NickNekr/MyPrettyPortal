import cx_Oracle

from config import app_config


class DataBase(object):
    def __init__(self):
        dsn = cx_Oracle.makedsn(
            app_config.HOST,
            app_config.PORT,
            service_name=app_config.SID,
        )
        self.conn = cx_Oracle.connect(
            user=app_config.USER,
            password=app_config.PASSWORD,
            dsn=dsn,
            encoding="UTF-8",
        )

    def __del__(self):
        self.conn.close()


oracle_db = DataBase() if app_config.ENV == "production" else None
