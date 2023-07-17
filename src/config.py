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

    PARQUET_PATH = "./duplication/data.parquet"

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

    EXCEL_FILE_PATH = "./duplication/database.xlsx"


class TestingConfig(Config):
    ENV = "testing"
    DEBUG = True


app_config = DevelopmentConfig()
