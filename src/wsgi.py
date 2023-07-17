from portal import create_app
from config import app_config

app = create_app()

if __name__ == "__main__":
    app.run(
        debug=app_config.FlaskApp.DEBUG,
        host=app_config.FlaskApp.HOST,
        port=app_config.FlaskApp.PORT,
    )
