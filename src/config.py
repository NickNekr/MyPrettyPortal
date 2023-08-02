import os
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

    GOLD_QUERY_PATH = "./Data/gold.sql"
    SILVER_QUERY_PATH = "./Data/silver.sql"

    with open(GOLD_QUERY_PATH, "r") as f:
        GOLD_QUERY = f.read()

    with open(SILVER_QUERY_PATH, "r") as f:
        SILVER_QUERY = f.read()

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
        PORT = 5000
        HOST = "0.0.0.0"
        DEBUG = True

        BASE_URL = f"http://{HOST}:{PORT}"

    class ResponseStatusCode(object):
        OK = 200
        NOT_FOUND = 404
        BAD_REQUEST = 400


class ProductionConfig(Config):
    ENV = "production"
    DEBUG = False


class DevelopmentConfig(Config):
    ENV = "development"
    DEBUG = True

    EXCEL_PATH = "./Data/database.xlsx"
    PARQUET_PATH = "./Data/database.parquet"


class TestingConfig(Config):
    ENV = "testing"
    DEBUG = True


app_config = DevelopmentConfig()
