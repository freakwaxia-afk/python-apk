#!/usr/bin/env bash
# 本地桌面预览：启动本地服务 + 用浏览器打开前端（不会编译 APK）。
set -euo pipefail
cd "$(dirname "$0")"
cd app
PYTHON="${PYTHON:-python3}"
exec "$PYTHON" main.py
