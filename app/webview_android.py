"""WebView 封装。

- Android：通过 pyjnius 调用系统原生 WebView（android.webkit.WebView），
  用 activity.setContentView 全屏接管界面并加载给定 URL。
  这是 Kivy 官方 wiki 验证过的做法，渲染与原生浏览器一致。
- 桌面：无法运行 Android 原生 WebView，改为打开默认浏览器做本地预览。
"""

import threading
import webbrowser

from kivy.utils import platform

ANDROID = platform == "android"


def launch_webview(url):
    """在 Android 上把原生 WebView 设为全屏内容并加载 url；桌面则打开浏览器。"""
    if ANDROID:
        _launch_android(url)
    else:
        threading.Timer(1.0, lambda: webbrowser.open(url)).start()


def _launch_android(url):
    from jnius import autoclass
    from android.runnable import run_on_ui_thread

    WebView = autoclass("android.webkit.WebView")
    WebViewClient = autoclass("android.webkit.WebViewClient")
    activity = autoclass("org.kivy.android.PythonActivity").mActivity

    @run_on_ui_thread
    def _show():
        wv = WebView(activity)
        settings = wv.getSettings()
        settings.setJavaScriptEnabled(True)        # 启用 JS
        settings.setDomStorageEnabled(True)        # 启用 localStorage
        settings.setUseWideViewPort(True)          # 支持 viewport meta
        settings.setLoadWithOverviewMode(True)
        settings.setAllowFileAccess(True)
        settings.setAllowContentAccess(True)
        wv.setWebViewClient(WebViewClient())
        # 用原生 WebView 全屏接管 Activity 内容
        activity.setContentView(wv)
        wv.loadUrl(url)

    _show()
