# AI / 同事接手指南：Python + WebView Android APK

> 本文档面向**同事和 AI 助手**，目标是让任何人（或 AI）无需口头沟通即可理解项目、自行构建 APK、排查常见问题、扩展后端接口。

---

## 1. 项目是什么

一个把 **Python(Flask) 本地服务 + 前端网页** 用 **原生 Android WebView** 全屏渲染打包成的 APK。
- 前端：纯 HTML/JS/CSS，放在 `app/www/`。
- 后端：Python Flask，跑在手机本机 `127.0.0.1:8080`，前端用 `fetch('/api/...')` 调用。
- 打包：用 [buildozer](https://github.com/kivy/buildozer) 把整个 `app/` 打成 Android APK。

**GitHub 仓库**
- 地址：`https://github.com/freakwaxia-afk/python-apk`
- 默认分支：`main`
- CI 工作流文件：`.github/workflows/build-apk.yml`

---

## 2. 仓库结构

```
python-webview-apk/
├── .github/workflows/build-apk.yml   # CI：构建并上传 APK 产物
├── app/
│   ├── main.py            # 入口：启动本地服务 + 拉起 WebView
│   ├── server.py          # Flask 本地服务（静态托管 + 加载后端路由）
│   ├── backend.py         # ★ 写后端 API 的地方（setup(app) 里注册路由）
│   ├── webview_android.py # 原生 WebView 封装（pyjnius）
│   └── www/
│       └── index.html     # 前端页面（含“调用 Python 后端”按钮示例）
├── buildozer.spec         # 打包配置（包名/权限/SDK 版本/依赖）
├── build_apk.sh           # 本地一键打包（用官方 Docker 镜像）
├── setup_vm.sh            # 在 Ubuntu 虚拟机里从零构建
├── run_desktop.sh         # 桌面预览
├── requirements.txt       # 仅桌面预览用依赖（CI/APK 不读这个）
└── AI_GUIDE.md            # 本文件
```

---

## 3. 如何触发构建 / 拿到 APK

**方式 A：推送到 `main` 分支（最常用）**
1. 把改动 `git push` 到 `main`。
2. GitHub Actions 自动运行 `.github/workflows/build-apk.yml`。
3. 构建完的 APK 作为 **Artifact** 上传：
   - 打开 `https://github.com/freakwaxia-afk/python-apk/actions`
   - 点进对应运行 → 页面底部 **Artifacts** 区 → 下载 `python-webview-apk` 压缩包
   - 解压得到 `pythonwebviewapp-debug.apk`（debug 签名，可直接 `adb install`）

**方式 B：手动触发**
- 在 Actions 页面选 `Build APK` → `Run workflow`。

**方式 C：本地构建（不需要 GitHub）**
- 有 Docker：`bash build_apk.sh`（用官方 `kivy/buildozer` 镜像）。
- 无 Docker 的 Ubuntu 虚拟机：`bash setup_vm.sh`。

> 注意：CI 用的是官方镜像直接 `docker run kivy/buildozer:latest android debug`，
> **不依赖**第三方的 `ArtemSBulgakov/buildozer-action`（那个 action 在新基础镜像上已坏，见第 5 节）。

---

## 4. 如何新增一个后端接口（给 AI / 同事的扩展步骤）

1. 编辑 `app/backend.py`，在 `setup(app)` 里加路由：
   ```python
   @app.route("/api/your_endpoint")
   def your_endpoint():
       return {"ok": True, "data": 42}
   ```
2. 前端在 `app/www/` 里用 `fetch('/api/your_endpoint')` 调用，记得 `await res.json()`。
3. 提交并推送到 `main`，CI 重新打包。

---

## 5. 已知坑（已修复，记录以防复发）

| 问题 | 根因 | 修复位置 |
|---|---|---|
| CI 报 `apt update ... 404 / exit code 100` | 第三方 `buildozer-action` 的 Dockerfile 给 Ubuntu resolute 加 `ppa:openjdk-r`（该 PPA 无 resolute 包） | 改用官方镜像直接构建，见 `build-apk.yml` |
| `Accept? (y/N)` 许可卡死、build-tools 装不上 | `android.accept_sdk_license = True` 被误放在 `[buildozer]` 段，应为 `[app]` 段 | `buildozer.spec` |
| 点击按钮报 `syntax error`、拿到的是网页不是 JSON | 静态兜底路由 `/<path:path>` 在旧版 Flask 下“吞掉”了 `/api/*` 接口，返回 `index.html` | `server.py`：后端路由在兜底路由**之前**注册；`buildozer.spec`：`flask` 改为 `flask>=3.0` 锁定新版路由行为 |

**排查口诀**：前端 `fetch` 报 JSON 解析错误时，先 `curl` 一下该接口看返回的是不是 `index.html` —— 是的话就是路由被兜底吞了。

---

## 6. 关键配置速查（buildozer.spec）

- `package.name = pythonwebviewapp` → 决定 APK 文件名。
- `android.api = 33` / `android.minapi = 21` / `android.ndk = 25b`
- `android.build_tools_version = 33.0.0` → 与 api 对齐，避免拉到过新的 37。
- `android.permissions = INTERNET` → WebView 访问网络必需。
- `android.accept_sdk_license = True` → **必须位于 `[app]` 段**。
- `requirements = python3,kivy,flask>=3.0,pyjnius` → APK 内 Python 依赖（不是 `requirements.txt`）。

---

## 7. 本地调试

- 桌面预览：`bash run_desktop.sh` 或 `python app/main.py`（会自动开浏览器）。
- 直接验证接口：`python -c "import server; server.start(8099); import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:8099/api/hello').read())"`。
