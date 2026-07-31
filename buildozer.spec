[app]

# 应用基本信息
title = 2048
package.name = game2048
package.domain = org.example

# 源码目录（main.py 必须在该目录根下）
source.dir = app
# 需要打包进 APK 的文件后缀（含前端资源）
source.include_exts = py,png,jpg,jpeg,kv,atlas,html,js,css,json,svg,woff,woff2,ttf,ico

# 版本
version = 1.0.0

# 依赖：python3 + hostpython3 必须同版本（钉到 3.11，避免镜像默认 3.14 与 kivy 2.3.1 编译不兼容）
# 注意：kivy/buildozer:latest 的默认 python3 / hostpython3 已升到 3.14，kivy 2.3.1 在 3.14 上无法编译
# （config.pxi 解析失败）；且 p4a 要求 python3 与 hostpython3 版本严格一致，所以两个都要钉。
requirements = python3==3.11.9,hostpython3==3.11.9,kivy==2.3.1,flask>=3.0,pyjnius

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
