"""在这里写你的 Python 后端逻辑。

main.py 启动时会自动 import 本文件并调用 setup(app)，
你可以往 Flask 的 app 上注册任意路由，前端通过 fetch 调用。

示例：前端 fetch('/api/hello') 会拿到下面的 JSON。
"""


def setup(app):
    @app.route("/api/hello")
    def hello():
        return {"message": "Hello from Python backend!", "ok": True}
