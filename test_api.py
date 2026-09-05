import pytest
import requests
import allure
from test_url_constants import *

@allure.feature("allure使用练习1")
class TestCase:

    @allure.story("登录成功与失败测试")
    @pytest.mark.smoke
    @pytest.mark.api
    @pytest.mark.parametrize("username,password,http_code,resp_code,fail_desc",[
        ("admin","123456",200,0,"账密正确但登录失败"),
        ("admin","AAA",200,1001,"密码错误但不是登录失败"),
        ("nobody","123456",404,1002,"用户不存在但不是登录失败")
    ])
    def test_login(self,username,password,http_code,resp_code,fail_desc):
        with allure.step("请求登录"):
            resp = requests.post(host+login_path, data={"username":username,"password":password})
        with allure.step("登录断言"):
            assert resp.status_code == http_code and resp.json()["code"] == resp_code , fail_desc


    @allure.story("订单带token查询成功测试")
    @pytest.mark.api
    def test_query_orders_success(self,session):
        with allure.step("订单查询请求"):
            query_result = session.get(host+orders_path)
        with allure.step("订单查询结果断言"):
            assert query_result.status_code == 200 and query_result.json()["code"] == 0 ,"存在token，查询订单未成功"

    @allure.story("订单不带token查询失败测试")
    @pytest.mark.api
    def test_query_orders_fail(self):
        with allure.step("订单查询请求"):
            query_result = requests.get(host+orders_path)
        with allure.step("订单查询结果断言"):
            assert query_result.status_code == 401 and query_result.json()["code"] == 2001 , "不存在token，查询订单成功"






