#!/usr/bin/env bash
# 一键打包 APK。
# 优先使用 Docker（官方 kivy/buildozer 镜像，免装 Android SDK/NDK）；
# 若本机没有 Docker，则回退到本机已安装的 buildozer。
#
# 镜像可覆盖：BUILDIZER_IMAGE=docker.xuanyuan.run/kivy/buildozer:latest ./build_apk.sh
# 权限：脚本在 root 下运行会自动加 --user 0（避免绑定挂载目录不可写）。
set -euo pipefail
cd "$(dirname "$0")"

IMAGE="${BUILDIZER_IMAGE:-kivy/buildozer:latest}"

# root 运行时让容器内也以 root 执行，避免对绑定挂载目录无写权限
DOCKER_USER_ARGS=()
if [ "$(id -u)" = "0" ]; then
  DOCKER_USER_ARGS+=(--user 0)
fi

if command -v docker >/dev/null 2>&1; then
  echo "==> 检测到 Docker，使用镜像 $IMAGE 构建 APK ..."
  docker run --rm "${DOCKER_USER_ARGS[@]}" \
    -v "$(pwd)":/home/user/hostcwd \
    -v buildozer_cache:/home/user/.buildozer \
    "$IMAGE" android debug
  echo "==> 构建完成，APK 位于 bin/ 目录。"
else
  echo "==> 未检测到 Docker，回退到本机 buildozer ..."
  if ! command -v buildozer >/dev/null 2>&1; then
    echo "错误：本机未安装 buildozer，也未安装 Docker。" >&2
    echo "请二选一：" >&2
    echo "  1) 安装 Docker：https://docs.docker.com/get-docker/" >&2
    echo "  2) pip install buildozer 并自行配置 Android SDK/NDK" >&2
    exit 1
  fi
  buildozer android debug
fi
