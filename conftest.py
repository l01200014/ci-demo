import pytest
import requests
from test_url_constants import *

@pytest.fixture(scope="session")
def login_resp():
    return requests.post(host + login_path, data={"username": "admin", "password": "123456"})

@pytest.fixture(scope="function")
def session(login_resp):
    session = requests.Session()
    session.headers.update({"Authorization": f"Bearer {login_resp.json()['token']}"})
    yield session
    session.close()