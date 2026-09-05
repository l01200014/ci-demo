import pytest
import allure
from test_url_constants import *

@allure.feature("allure使用练习2")
@allure.story("订单带token查询")
@pytest.mark.api
def test_orders_with_session(session):
    query_result = session.get(host + orders_path)
    assert query_result.status_code == 200 and query_result.json()["code"] == 0, "存在token，查询订单未成功"



