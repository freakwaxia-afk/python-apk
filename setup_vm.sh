#!/usr/bin/env bash
# ============================================================================
#  VirtualBox / WSL2 Ubuntu x86-64 一键构建 Android APK
#  用法: 在 VirtualBox 里的 Ubuntu 22.04 (x86-64) 虚拟机中:
#        tar -xzf python-webview-apk-src.tar.gz && cd python-webview-apk
#        bash setup_vm.sh
#  需要: 联网 (首次会下载 Android SDK/NDK, 约 10-15GB)
#  产物: bin/<app>-debug.apk
# ============================================================================
set -euo pipefail

cd "$(dirname "$0")"

echo "==> [1/4] 安装系统依赖 (需要 sudo/root) ..."
SUDO=""
if [ "$(id -u)" != "0" ]; then
  SUDO="sudo"
fi
$SUDO apt update
$SUDO apt install -y python3 python3-pip python3-venv git zip unzip \
  openjdk-17-jdk curl build-essential libffi-dev libssl-dev

echo "==> [2/4] 创建 Python 虚拟环境并安装构建工具 ..."
python3 -m venv venv
# shellcheck disable=SC1091
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt buildozer

echo "==> [3/4] 构建 APK (buildozer android debug) ..."
echo "    首次构建会自动下载 Android SDK/NDK，请耐心等待 (10-15GB)。"
buildozer android debug

echo "==> [4/4] 完成。"
APK=$(ls -1 bin/*.apk 2>/dev/null | head -n1 || true)
if [ -n "$APK" ]; then
  echo "APK 已生成: $(pwd)/$APK"
  echo "安装到手机: adb install \"$APK\""
else
  echo "未找到 bin/*.apk，请检查上面的构建日志。"
  exit 1
fi
