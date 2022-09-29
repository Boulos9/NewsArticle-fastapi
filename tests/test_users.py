import pytest
from jose import jwt
from app import schemas
from app.config import get_settings
from jose import JWTError

settings = get_settings()

#####create_user#####

def test_create_user(client):
    # will search for post operation, with '/users/' as path
    response = client.post("/users/", json={"email": "hello@gmail.com", "password": "pass123"})
    new_user = schemas.UserOut(**response.json())
    assert new_user.email == "hello@gmail.com"
    assert response.status_code == 201
    id = new_user.id

    # get the created user
    response = client.get(f"/users/{id}")
    assert response.status_code == 200
    new_user = schemas.UserOut(**response.json())
    assert new_user.email == "hello@gmail.com"
    assert new_user.id == id


def test_create_existed_email(client,test_user1):
    response = client.post("/users/", json={"email": "hello@gmail.com", "password": "pass123"})
    assert response.status_code == 422
    assert response.json()['detail'] == "email: hello@gmail.com already exists"


def test_create_invalid_email(client):
    response = client.post("/users/", json={"email": "hello@@gmailcom", "password": "pass123"})
    assert response.status_code == 422 # unprocessable entity


def test_create_invalid_password(client):
    response = client.post("/users/", json={"email": "hello@gmail.com", "password": "pass"})
    assert response.status_code == 422


#####get_user#####

def test_get_user(client, test_user1):
    response = client.get(f"/users/{1}")
    assert response.status_code == 200
    user = response.json()
    assert user["email"] == test_user1["email"]
    assert user["id"] == test_user1["id"]


def test_get_non_existing_user(client):
    response = client.get(f"/users/{1234}")
    assert response.status_code == 404
    assert response.json()["detail"] == "user with id: 1234 was NOT FOUND"


@pytest.mark.parametrize("id, status_code",[
                            (0,422),
                            ("abc",422)])
def test_get_invalid_user_id(client,id,status_code):
    response = client.get(f"/users/{id}")
    # print(response.json())
    assert response.status_code == status_code


#####login#####

def test_login_user(client, test_user1): # test_user1 is a fixture in conftest
    response = client.post("/login", data={"username": test_user1["email"], 
                                             "password": test_user1["password"]})
    # validate the token
    """
        **response.json() -> {"access_token": 'the.jwt.token', "token_type": "bearer"}
    """
    login_res = schemas.Token(**response.json()) # pydantic model instead of dict
    payload = jwt.decode(login_res.access_token, settings.secret_key, algorithms=settings.algorithm)
    id = payload.get("user_id")
    assert id == test_user1['id']
    assert login_res.token_type == "bearer"
    assert response.status_code == 200


@pytest.mark.parametrize("email, password, status_code", 
                            [('invalidEmail@gmail.com',"pass123", 401),
                            ("hello@gmail.com", "invalidpass", 401),
                            ("invalidEmail@gmail.com", "invalidpass", 401),
                            (None, 'pass123', 422),
                            ("hello@gmail.com", None, 422)])
def test_incorrect_login(test_user1, client, email, password, status_code):
    response = client.post("/login", data={"username": email, 
                                             "password": password})
    assert response.status_code == status_code