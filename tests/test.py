import requests
from src.config import app_config


class JsonTestData:
    add_data = {
        "user": {
            "LOGIN": "nnnekr",
            "LAST_NAME": "Nekrasov",
            "FIRST_NAME": "Nikolay",
            "SECOND_NAME": "Nikolaevich",
            "SNILS": "127-001",
        },
        "specs": [
            {
                "SPEC_CODE": 10,
                "SPEC_NAME": "Терапевт",
            },
            {
                "SPEC_CODE": 11,
                "SPEC_NAME": "Онколог",
            },
        ],
    }

    test_mess = {"message": "Hello, DIT!"}

    user_founded = {"message": "User founded!"}
    user_not_founded = {"message": "User not founded!"}
    user_added = {"message": "User added!"}
    user_deleted = {"message": "User deleted!"}

    spec_added = {"message": "Spec added!"}
    spec_deleted = {"message": "Spec deleted!"}
    spec_founded = {"message": "Spec founded!"}
    spec_not_founded = {"message": "Spec not founded!"}

    user_spec_added = {"message": "User to spec added!"}
    user_spec_not_founded = {"message": "User spec not founded!"}
    user_spec_founded = {"message": "User spec founded!"}


def test_hello_world():
    response = requests.get(f"{app_config.Web.BASE_URL}/data/test")
    assert response.status_code == app_config.ResponseStatusCode.OK
    assert response.json() == JsonTestData.test_mess

    response = requests.get(f"{app_config.Web.BASE_URL}/celery/test")
    assert response.status_code == app_config.ResponseStatusCode.OK
    assert response.json() == JsonTestData.test_mess


def test_add_and_delete_cascade_user():
    response = requests.post(
        f"{app_config.Web.BASE_URL}/data",
        json=JsonTestData.add_data["user"],
    )
    assert response.status_code == app_config.ResponseStatusCode.OK
    json_response = response.json()
    user_id = json_response["user_id"]
    assert json_response["message"] == JsonTestData.user_added["message"]

    response = requests.get(f"{app_config.Web.BASE_URL}/data/{user_id}")
    assert response.status_code == app_config.ResponseStatusCode.OK
    json_response = response.json()
    assert json_response["message"] == JsonTestData.user_founded["message"]
    assert json_response["user"] == JsonTestData.add_data["user"]

    response = requests.delete(f"{app_config.Web.BASE_URL}/data/{user_id}")
    assert response.status_code == app_config.ResponseStatusCode.OK
    assert response.json() == JsonTestData.user_deleted

    response = requests.get(f"{app_config.Web.BASE_URL}/data/{user_id}")
    assert response.status_code == app_config.ResponseStatusCode.NOT_FOUND
    assert response.json() == JsonTestData.user_not_founded
