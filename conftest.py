import pytest
import requests
import allure
from test_url_constants import *

@allyre.feature("数据准备")
@allure.story("登录")
@pytest.fixture(scope="session")
def login_resp():
    return requests.post(host + login_path, data={"username": "admin", "password": "123456"})

@allyre.feature("数据准备")
@allure.strory("获取登录token新建session")
@pytest.fixture(scope="function")
def session(login_resp):
    session = requests.Session()
    session.headers.update({"Authorization": f"Bearer {login_resp.json()['token']}"})
    yield session
    session.close()