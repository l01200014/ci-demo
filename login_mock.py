# -*- coding: utf-8 -*-
"""
Day 15 本地 Mock 登录服务（教学用）
- 零依赖：仅使用 Python 内置库 http.server
- 模拟真实后端：登录接口"状态码 + 业务码"双通道返回
- 启动：python login_mock.py 8000
- 访问：浏览器打开 http://127.0.0.1:8000/login

设计意图（教学考点）：
1. 正确账密 -> 200 + {"code": 0, "msg": "登录成功", "token": "..."}
2. 密码错误 -> 200 + {"code": 1001, "msg": "密码错误"}   <- 状态码 200 但业务失败！
3. 用户不存在 -> 404 + {"code": 1002, "msg": "用户不存在"} <- 状态码也报错
4. 缺少字段 -> 400 + {"code": 1003, "msg": "参数缺失"}
   让学习者亲手抓到"200 但业务失败"的真实案例
"""

import json
import sys
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

# 模拟用户数据库
USERS = {
    "admin": "123456",
    "test": "abc123",
}

# 已签发的有效 token 集合（模拟服务端会话表）
TOKENS = set()

LOGIN_PAGE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="utf-8">
    <title>Mock 登录页 - Day 15 抓包练习</title>
</head>
<body>
    <h2>Mock 登录页（本地服务，随便抓包）</h2>
    <form action="/api/login" method="post">
        <p>用户名：<input type="text" name="username" value="admin"></p>
        <p>密码：<input type="password" name="password" value="123456"></p>
        <p><input type="submit" value="登录"></p>
    </form>
    <p style="color:gray">已知账号：admin/123456、test/abc123；<br>
    故意输错密码试试，观察返回的状态码和 Body。</p>
</body>
</html>
"""


class MockHandler(BaseHTTPRequestHandler):
    # 关闭默认的日志格式，改用自定义更清晰的输出
    def log_message(self, format, *args):
        pass

    def _send_json(self, status_code, body: dict):
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _send_html(self, body: str, status_code: int = 200):
        data = body.encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _read_form(self):
        """读取表单请求体（application/x-www-form-urlencoded）"""
        length = int(self.headers.get("Content-Length", 0) or 0)
        raw = self.rfile.read(length).decode("utf-8") if length else ""
        return {k: v[0] for k, v in parse_qs(raw).items()}

    def _print_request(self, body_dict: dict):
        """打印请求摘要，方便学习者对照 DevTools 观察"""
        print("-" * 60)
        print(f"[请求] {self.command} {self.path}")
        print(f"[请求头] Content-Type: {self.headers.get('Content-Type')}")
        print(f"[请求体] {body_dict}")
        print(f"[请求头] User-Agent: {self.headers.get('User-Agent', '')[:50]}...")

    def _check_token(self):
        """校验 Authorization: Bearer <token>，返回 (是否通过, token)"""
        auth = self.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            print("[鉴权] 401 -> 缺少 Authorization: Bearer <token> 头")
            self._send_json(401, {"code": 2001, "msg": "未认证：缺少 Authorization 头"})
            return False, None
        token = auth[len("Bearer "):].strip()
        if token not in TOKENS:
            print("[鉴权] 401 -> token 无效")
            self._send_json(401, {"code": 2002, "msg": "token 无效或已过期"})
            return False, None
        print("[鉴权] 通过 -> token 有效")
        return True, token

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/login":
            self._print_request({})
            self._send_html(LOGIN_PAGE)
            return

        # 受保护接口：需要登录拿到的 token
        if path == "/api/orders":
            ok, _ = self._check_token()
            if not ok:
                return
            print("[响应] 200 -> 返回订单列表")
            self._send_json(200, {
                "code": 0,
                "msg": "订单列表",
                "orders": [
                    {"id": 1, "amount": 99.0, "status": "pending"},
                    {"id": 2, "amount": 199.0, "status": "completed"},
                    {"id": 3, "amount": 299.0, "status": "pending"},
                ]
            })
            return
        self._send_json(404, {"code": 1004, "msg": f"接口不存在: {path}"})

    def do_POST(self):
        path = urlparse(self.path).path
        form = self._read_form()
        self._print_request(form)

        if path == "/api/login":
            username = form.get("username")
            password = form.get("password")

            # 参数缺失 -> 400（状态码层面就报错）
            if not username or not password:
                print("[响应] 400 -> 参数缺失")
                self._send_json(400, {"code": 1003, "msg": "参数缺失: 需要 username 和 password"})
                return

            # 用户不存在 -> 404（状态码层面就报错）
            if username not in USERS:
                print("[响应] 404 -> 用户不存在")
                self._send_json(404, {"code": 1002, "msg": "用户不存在"})
                return

            # 密码错误 -> 200 + 业务码 1001（重点：状态码成功，业务失败！）
            if USERS[username] != password:
                print("[响应] 200 -> 业务失败 code=1001 (密码错误)")
                self._send_json(200, {"code": 1001, "msg": "密码错误"})
                return

            # 登录成功
            token = f"mock-token-{uuid.uuid4().hex[:16]}"
            TOKENS.add(token)
            print("[响应] 200 -> 登录成功 code=0, 已签发 token")
            self._send_json(200, {
                "code": 0,
                "msg": "登录成功",
                "token": token,
                "user": {"username": username, "role": "tester"}
            })
            return

        self._send_json(404, {"code": 1004, "msg": f"接口不存在: {path}"})


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    server = ThreadingHTTPServer(("127.0.0.1", port), MockHandler)
    print(f"Mock 登录服务已启动: http://127.0.0.1:{port}/login")
    print("按 Ctrl+C 停止服务")
    server.serve_forever()


if __name__ == "__main__":
    main()
