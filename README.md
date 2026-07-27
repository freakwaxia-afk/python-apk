# Python + WebView → APK 打包模板

把 Python 代码（后端）+ 网页前端（HTML/JS/CSS）打包成一个 Android APK，
App 内用 **Android 原生 WebView** 全屏渲染你的网页，网页通过 `fetch` 调用本地 Python 后端。

- 打包工具：**Buildozer**（默认用官方 `kivy/buildozer` Docker 镜像，免装 Android SDK/NDK）
- 界面载体：**Kivy** + 通过 `pyjnius` 嵌入系统原生 WebView
- 内容来源：Python（Flask）在 `127.0.0.1` 起本地服务，托管 `app/www/`，WebView 加载 `http://127.0.0.1`

---

## 目录结构

```
python-webview-apk/
├── build_apk.sh            # 一键打包脚本（自动判断 Docker / 本机 buildozer）
├── run_desktop.sh          # 本地桌面预览（浏览器打开，不编译 APK）
├── buildozer.spec          # Buildozer 配置（应用名、权限、依赖等）
├── extra_manifest_app.xml  # 允许明文 HTTP（Android 9+ 连本地服务需要）
├── requirements.txt        # 本地桌面开发依赖
└── app/
    ├── main.py             # 入口：启动服务 + 嵌入 WebView（一般不用改）
    ├── server.py           # 本地 HTTP 服务（托管 www/ + 加载 backend.py）
    ├── webview_android.py  # 原生 WebView 封装（Android） / 桌面回退浏览器
    ├── backend.py          # 👉 你的 Python 后端逻辑写这里
    └── www/
        └── index.html      # 👉 你的前端写这里（可放整个前端项目）
```

---

## 怎么用（三步）

### 1. 放入你的代码
- **前端**：把 HTML/JS/CSS 放进 `app/www/`（可直接替换 `index.html`，或整体放一个前端工程）。
- **后端**：在 `app/backend.py` 的 `setup(app)` 里注册路由，例如：
  ```python
  def setup(app):
      @app.route("/api/hello")
      def hello():
          return {"message": "Hello from Python!"}
  ```
  前端用 `fetch('/api/hello')` 调用即可。

> 想跑任意 Python 逻辑？直接在 `setup(app)` 里写，或把函数挂到路由上由前端触发。

### 2. 本地预览（可选）
```bash
pip install -r requirements.txt
./run_desktop.sh          # 启动本地服务并打开浏览器预览 http://127.0.0.1:8080
```

### 3. 打包 APK
```bash
./build_apk.sh
```
- 有 **Docker**：自动拉取 `kivy/buildozer` 镜像并在容器内编译，产物在 `bin/*.apk`。
- 没 **Docker** 但装了 buildozer：回退到本机编译（需自行配置 Android SDK/NDK）。
- 首次构建会下载 SDK/NDK 等，耗时较长（几分钟到几十分钟），后续有缓存会快很多。

把 `bin/*.apk` 推到手机安装即可。

---

## 常见问题 / 注意事项

- **本地服务用 `http://127.0.0.1`**：Android 9+ 默认禁止明文 HTTP，`extra_manifest_app.xml`
  里的 `usesCleartextTraffic="true"` 已放开；只连本机回环，不会暴露到外部网络。
- **权限**：`buildozer.spec` 已加 `INTERNET`（WebView 访问网络必须）。若要访问文件/相机等，
  在 `android.permissions` 里追加对应权限。
- **改应用名/包名**：编辑 `buildozer.spec` 的 `title`、`package.name`、`package.domain`
  （`package.name` 只能小写字母和数字）。
- **换端口**：改 `app/main.py` 顶部的 `PORT`（默认 8080）和 `server.py` 默认值。
- **WebView 全屏接管**：本方案用 `activity.setContentView(webview)` 让原生 WebView 占满全屏，
  因此页面自身要负责完整 UI（含返回键等交互，可监听 JS 桥或系统返回）。
- **桌面无法跑原生 WebView**：`run_desktop.sh` 仅用浏览器预览，真正效果以 APK 为准。

---

## 构建失败排查

- **Docker 权限问题**：若报目录写权限错误，可给镜像加 `--user $(id -u):$(id -g)`，
  或用 `--user 0` 以 root 运行（见 `build_apk.sh` 顶部的 IMAGE 注释）。
- **依赖编译慢/失败**：`flask` 是纯 Python，通常没问题；若加 C 扩展依赖，需确认 p4a 有对应 recipe。
- 详细日志：把 `buildozer.spec` 的 `log_level` 改为 `2`（已默认），或在 `build_apk.sh` 命令后加 `-v`。

---

## 转交给同事

### 1. 把项目交出去
推荐用 git；或直接打包（已排除构建产物/日志）：
```bash
cd /root/python-webview-apk
tar --exclude='.buildozer' --exclude='build.log' --exclude='pull.log' \
    --exclude='__pycache__' --exclude='.git' --exclude='bin' \
    -czf python-webview-apk.tar.gz .
# 发给同事后，对方解压即可
```
> 不需要把 `.buildozer/`（p4a 缓存）、`build.log`、`bin/` 传过去，对方首次构建会自己重新下载。

### 2. 同事怎么跑起来
- **正常网络（能连 Docker Hub）**：直接 `./build_apk.sh`，自动拉 `kivy/buildozer` 并出包。
- **受限网络（连不上 Docker Hub）**：用可达镜像，例如你提供的轩辕镜像（需先登录）：
  ```bash
  docker login docker.xuanyuan.run      # 用官网注册账号登录
  BUILDIZER_IMAGE=docker.xuanyuan.run/kivy/buildozer:latest ./build_apk.sh
  ```
- 没有 Docker：本机装 `buildozer` + Android SDK/NDK，再 `./build_apk.sh`（脚本会自动回退到本机 buildozer）。

### 3. 同事怎么放自己的代码
和“怎么用”三步一样：前端丢 `app/www/`、Python 后端写 `app/backend.py` 的 `setup(app)`、
要加 Python 依赖就改 `buildozer.spec` 的 `requirements`。改完重跑 `./build_apk.sh`。
产出的 APK 在 `bin/`，用 `adb install bin/*.apk` 或拷到手机安装。

### 4. 脚本的自动兼容
`build_apk.sh` 已做两件事，无需同事改代码：
- 镜像可通过环境变量 `BUILDIZER_IMAGE` 覆盖；
- 在 root 下运行会自动加 `--user 0`（避免绑定挂载目录无写权限），普通用户则不加。
