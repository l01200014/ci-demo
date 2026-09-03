import requests

def test_smoke():
    """CI链路冒烟:验证环境与pytest正常"""
    assert 1+1 == 2

def test_requests_installed():
    assert requests.__version__

