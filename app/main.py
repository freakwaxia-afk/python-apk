"""应用入口（Buildozer 在 Android 上会运行本文件）。

工作流程：
  1. 启动本地 HTTP 服务（托管 app/www 下的前端，并加载 app/backend.py 的后端路由）
  2. 等服务就绪后，用原生 WebView 全屏加载 http://127.0.0.1:PORT

你通常不需要改本文件，只要：
  - 把前端放进  app/www/
  - 把 Python 后端逻辑写进  app/backend.py 的 setup(app)
  - 运行  ./build_apk.sh  打包 APK
"""

import server
import webview_android

PORT = 8080
URL = f"http://127.0.0.1:{PORT}"


def main():
    # 1) 启动本地 HTTP 服务（后台线程）
    server.start(port=PORT)
    server.wait_until_ready(port=PORT, timeout=10)

    if webview_android.ANDROID:
        # 2) Android：用 Kivy App 作为载体，在 on_start 中嵌入原生 WebView
        from kivy.app import App
        from kivy.uix.widget import Widget
        from kivy.clock import Clock

        class Root(Widget):
            pass

        class MainApp(App):
            def build(self):
                return Root()

            def on_start(self):
                Clock.schedule_once(lambda dt: webview_android.launch_webview(URL), 0)

        MainApp().run()
    else:
        # 2) 桌面预览：直接打开浏览器（桌面无法运行 Android 原生 WebView）
        webview_android.launch_webview(URL)
        import time
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
