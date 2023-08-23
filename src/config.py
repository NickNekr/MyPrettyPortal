import os
from celery.schedules import crontab
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv()


class Config(object):
    TZ = os.environ.get("DB_TIMEZONE")

    HOST = os.environ.get("DB_HOST")
    DB = os.environ.get("DB_NAME")
    USERNAME = os.environ.get("DB_USER")
    PORT = os.environ.get("DB_PORT")
    PASSWORD = os.environ.get("DB_PASSWORD")
    SQLALCHEMY_DATABASE_URI = f"postgresql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DB}"

    class DataBase(object):
        HOST = os.environ.get("SUPP_DB_HOST")
        PORT = os.environ.get("SUPP_DB_PORT")
        SID = os.environ.get("SUPP_DB_SID")
        USER = os.environ.get("SUPP_DB_USERNAME")
        PASSWORD = os.environ.get("SUPP_DB_PASS")

        GOLD_QUERY_PATH = "/web/src/apps/services/oracle_services/Queries/gold.sql"
        SILVER_QUERY_PATH = "/web/src/apps/services/oracle_services/Queries/silver.sql"

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
            self.GOLD_QUERY = f.read()

        with open(self.DataBase.SILVER_QUERY_PATH, "r") as f:
            self.SILVER_QUERY = f.read()

    ENV = "production"
    DEBUG = False


class DevelopmentConfig(Config):
    ENV = "development"
    DEBUG = True

    EXCEL_FILE_PATH = "/web/Data/database.xlsx"
    PARQUET_PATH = "/web/Data/database.parquet"


class TestingConfig(Config):
    ENV = "testing"
    DEBUG = True


app_config = DevelopmentConfig()
