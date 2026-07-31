"""应用入口（Buildozer 在 Android 上会运行本文件）。

工作流程：
  1. 启动本地 HTTP 服务（托管 app/www 下的前端，并加载 app/backend.py 的后端路由）
  2. 等服务就绪后，用原生 WebView 全屏加载 http://127.0.0.1:PORT

你通常不需要改本文件，只要：
  - 把前端放进  app/www/
  - 把 Python 后端逻辑写进  app/backend.py 的 setup(app)
  - 运行  ./build_apk.sh  打包 APK

注意：本文件已加入“启动崩溃自检”——任何启动期的异常都会被捕获，
完整 traceback 写入 /sdcard/2048_crash.txt，并尽量显示在屏幕上（方便无 adb 时截图排查）。
"""

import traceback

PORT = 8080
URL = "http://127.0.0.1:%d" % PORT

# 屏幕上用于显示错误的 Kivy Label（若 Kivy 成功启动则会存在）
_label = None


def _write_crash(tb):
    try:
        with open("/sdcard/2048_crash.txt", "w") as f:
            f.write(tb)
    except Exception:
        pass


def show_error():
    """捕获当前异常并尽量暴露出来：写文件 + 屏幕 Label + Android Toast。"""
    tb = traceback.format_exc()
    _write_crash("2048 crash:\n" + tb)
    # 1) 屏幕 Label（若 Kivy 已起来）
    try:
        global _label
        if _label is not None:
            _label.text = "2048 启动失败（请截图发我）:\n\n" + tb
    except Exception:
        pass
    # 2) Android Toast
    try:
        from jnius import autoclass
        from android.runnable import run_on_ui_thread

        activity = autoclass("org.kivy.android.PythonActivity").mActivity
        Toast = autoclass("android.widget.Toast")

        @run_on_ui_thread
        def _t():
            Toast.makeText(
                activity,
                "2048 crashed - 截图或看 /sdcard/2048_crash.txt",
                Toast.LENGTH_LONG,
            ).show()

        _t()
    except Exception:
        pass


def main():
    global _label
    # 延迟导入，避免 import 阶段报错导致入口 try/except 无法接住
    import server
    import webview_android

    if webview_android.ANDROID:
        from kivy.app import App
        from kivy.uix.label import Label
        from kivy.clock import Clock

        class MainApp(App):
            def build(self):
                global _label
                _label = Label(
                    text="正在启动 2048 …\n(请稍候)",
                    halign="left",
                    valign="top",
                )
                _label.bind(size=_label.setter("text_size"))
                return _label

            def on_start(self):
                def doit(dt):
                    try:
                        server.start(port=PORT)
                        server.wait_until_ready(port=PORT, timeout=10)
                        webview_android.launch_webview(URL)
                    except Exception:
                        show_error()

                Clock.schedule_once(doit, 0)

        try:
            MainApp().run()
        except Exception:
            show_error()
    else:
        # 桌面预览：直接打开浏览器（桌面无法运行 Android 原生 WebView）
        try:
            server.start(port=PORT)
            server.wait_until_ready(port=PORT, timeout=10)
        except Exception:
            show_error()
            return
        webview_android.launch_webview(URL)
        import time
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    try:
        main()
    except Exception:
        show_error()
