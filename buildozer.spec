[app]

# 应用基本信息
title = PythonWebViewApp
package.name = pythonwebviewapp
package.domain = org.example

# 源码目录（main.py 必须在该目录根下）
source.dir = app
# 需要打包进 APK 的文件后缀（含前端资源）
source.include_exts = py,png,jpg,jpeg,kv,atlas,html,js,css,json,svg,woff,woff2,ttf,ico

# 版本
version = 1.0.0

# 依赖：python3 + kivy(界面载体) + flask(本地HTTP服务) + pyjnius(调用原生WebView)
requirements = python3,kivy,flask>=3.0,pyjnius

# 屏幕方向 / 全屏
orientation = portrait
fullscreen = 0

# Android 权限：WebView 访问网络（含本地 127.0.0.1）需要 INTERNET
android.permissions = INTERNET

# 允许明文 HTTP（Android 9+ 默认禁止），以便 WebView 加载 http://127.0.0.1
android.extra_manifest_application_arguments = extra_manifest_app.xml

# Android 编译版本（如需调整可改）
android.api = 33
android.minapi = 21
android.ndk = 25b

# Auto-accept Android SDK licenses (needed for non-interactive builds)
# NOTE: this must live in the [app] section, not [buildozer], or it is ignored.
android.accept_sdk_license = True
# Pin build-tools to match api=33 (avoids pulling bleeding-edge 37)
android.build_tools_version = 33.0.0

[buildozer]
log_level = 2
warn_on_root = 0
