import pytest
from test_url_constants import *

@pytest.mark.api
def test_orders_with_session(session):
    query_result = session.get(host + orders_path)
    assert query_result.status_code == 200 and query_result.json()["code"] == 0, "存在token，查询订单未成功"



