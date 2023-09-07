import os
from celery.schedules import crontab
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv()


class Consistency(object):
    def __init__(self, id_name, id, value_name, value) -> None:
        self.id_name = id_name
        self.id = id
        self.value_name = value_name
        self.value = value


class Config(object):
    TZ = os.environ.get("DB_TIMEZONE")

    HOST = os.environ.get("DB_HOST")
    DB = os.environ.get("DB_NAME")
    USERNAME = os.environ.get("DB_USER")
    PORT = os.environ.get("DB_PORT")
    PASSWORD = os.environ.get("DB_PASSWORD")
    SQLALCHEMY_DATABASE_URI = f"postgresql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DB}"

    PARQUET_PATH = "/web/Data/database.parquet"

    class UniqueTest:
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

    NOT_CONSISTENT_DATA = {
        "USER_ROLE_ID": [
            {
                "USER_ROLE_ID": 21,
            },
            {
                "USER_ROLE_ID": 31,
            },
            {
                "USER_ROLE_ID": 101,
            },
        ],
        "LPU_ID": [],
        "MO_ID": [],
        "SPEC_CODE": [],
    }

    CONSISTENT_DATA = [
        Consistency("USER_ROLE_ID", 31, "USER_ROLE", "Регистратор ЛЛО"),
        Consistency("USER_ROLE_ID", 21, "USER_ROLE", "Администратор ЛЛО"),
        Consistency("USER_ROLE_ID", 101, "USER_ROLE", "Специалист по ЗК"),
    ]

    class DataBase(object):
        HOST = os.environ.get("SUPP_DB_HOST")
        PORT = os.environ.get("SUPP_DB_PORT")
        SID = os.environ.get("SUPP_DB_SID")
        USER = os.environ.get("SUPP_DB_USERNAME")
        PASSWORD = os.environ.get("SUPP_DB_PASS")

        GOLD_QUERY_PATH = "/web/src/apps/services/oracle_db_services/Queries/gold.sql"

    TABLES_LIST = [
        "role",
        "lpus",
        "specialities",
        "users_to_role",
        "users_to_specialisation",
        "users_to_lpu",
        "lpus_to_mo",
        "users_additional_info",
        "users",
    ]

    class FlaskApp(object):
        PORT = 5089
        HOST = "0.0.0.0"
        DEBUG = True

        BASE_URL = f"http://{HOST}:{PORT}"

    class ResponseStatusCode(object):
        OK = 200
        NOT_FOUND = 404
        BAD_REQUEST = 400

    class CeleryConfig(object):
        broker_url = "redis://redis:6379/0"

        imports = ("apps.services.celery_services.tasks",)

        broker_connection_retry_on_startup = True

        timezone = "Europe/Moscow"

        beat_schedule = {
            "my-scheduled-task": {
                "task": "apps.services.celery_services.tasks.update_data",
                "schedule": crontab(minute="0", hour="9"),
            },
        }

        beat_schedule_timezone = "Europe/Moscow"


class ProductionConfig(Config):
    def __init__(self):
        with open(self.DataBase.GOLD_QUERY_PATH, "r") as f:
            self.DataBase.GOLD_QUERY = f.read()  # pyright: ignore

    ENV = "production"
    DEBUG = False


class DevelopmentConfig(Config):
    ENV = "development"
    DEBUG = True

    EXCEL_FILE_PATH = "/web/Data/database.xlsx"


class TestingConfig(Config):
    ENV = "testing"
    DEBUG = True


app_config = DevelopmentConfig()
