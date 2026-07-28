"""本地 HTTP 服务。

- 托管 app/www 下的静态前端（HTML/JS/CSS/图片等）。
- 若 app/backend.py 存在，会 import 它并调用 setup(app)，
  你可以在里面往 Flask 的 app 上注册任意后端路由，前端用 fetch 调用。
- 未匹配到静态文件时（如前端路由 / SPA）回退到 index.html。
"""

import os
import threading
import time
import urllib.request

_HERE = os.path.dirname(os.path.abspath(__file__))
WWW_DIR = os.path.join(_HERE, "www")


def start(port=8080, host="127.0.0.1", www_dir=None):
    from flask import Flask, send_from_directory

    www = www_dir or WWW_DIR
    app = Flask(__name__, static_folder=None)

    # 先加载后端路由，确保 /api/* 等接口优先于下面的静态文件兜底路由匹配，
    # 否则旧版 Flask/Werkzeug 下兜底路由会“吞掉” /api/* 并返回 index.html（即按钮报 syntax error）。
    _load_backend(app)

    @app.route("/")
    @app.route("/<path:path>")
    def serve(path="index.html"):
        target = os.path.join(www, path)
        if os.path.isfile(target):
            return send_from_directory(www, path)
        # 未匹配到静态文件（如 SPA 路由）时回退到 index.html
        return send_from_directory(www, "index.html")

    t = threading.Thread(
        target=lambda: app.run(
            host=host, port=port, debug=False, use_reloader=False, threaded=True
        ),
        daemon=True,
    )
    t.start()
    return app


def _load_backend(app):
    path = os.path.join(_HERE, "backend.py")
    if not os.path.exists(path):
        return
    import importlib.util

    spec = importlib.util.spec_from_file_location("user_backend", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if hasattr(mod, "setup"):
        mod.setup(app)


def wait_until_ready(port=8080, host="127.0.0.1", timeout=10):
    url = f"http://{host}:{port}/"
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            urllib.request.urlopen(url, timeout=1)
            return True
        except Exception:
            time.sleep(0.2)
    return False
