#!/bin/bash

# 安装libcamera库的一键脚本
# 适用于Ubuntu系统
# 此脚本将从源码构建并安装libcamera及其依赖项

# 设置错误处理：发生错误时立即退出
set -e

# 函数：显示信息消息
echo_info() {
    echo "\033[1;34m[INFO]\033[0m $1"
}

# 函数：显示成功消息
echo_success() {
    echo "\033[1;32m[SUCCESS]\033[0m $1"
}

# 函数：显示错误消息
echo_error() {
    echo "\033[1;31m[ERROR]\033[0m $1"
}

# 检查是否以root用户运行
if [ "$EUID" -ne 0 ]; then 
    echo_error "请以root用户运行此脚本（使用sudo）"
    exit 1
fi

# 更新系统包
echo_info "更新系统包..."
apt update && apt upgrade -y

# 安装必要的依赖项
echo_info "安装构建依赖项..."
apt install -y \n    git \n    build-essential \n    meson \n    ninja-build \n    pkg-config \n    libyaml-dev \n    python3-yaml \n    python3-ply \n    python3-jinja2 \n    libgstreamer1.0-dev \n    libgstreamer-plugins-base1.0-dev \n    libgstreamer-plugins-bad1.0-dev \n    gstreamer1.0-plugins-base \n    gstreamer1.0-plugins-good \n    gstreamer1.0-plugins-bad \n    gstreamer1.0-plugins-ugly \n    gstreamer1.0-libav \n    gstreamer1.0-tools \n    libudev-dev \n    libexif-dev \n    libjpeg-dev \n    libtiff-dev \n    cmake

# 安装相机特定依赖项（适用于树莓派等平台）
echo_info "安装相机特定依赖项..."
apt install -y \n    libdrm-dev \n    libgbm-dev \n    libgles2-mesa-dev \n    libinput-dev \n    libudev-dev \n    libxkbcommon-dev \n    wayland-protocols

# 创建临时构建目录
echo_info "创建构建目录..."
BUILD_DIR="/tmp/libcamera_build"
rm -rf "$BUILD_DIR" || true
mkdir -p "$BUILD_DIR"
cd "$BUILD_DIR"

# 克隆libcamera仓库
echo_info "克隆libcamera仓库..."
git clone https://git.libcamera.org/libcamera/libcamera.git
cd libcamera

# 初始化子模块
echo_info "初始化子模块..."
git submodule update --init

# 创建构建目录
mkdir -p build
cd build

# 配置构建
echo_info "配置libcamera构建..."
meson setup \n    -Dpipelines=all \n    -Dtest=false \n    -Ddocumentation=false \n    ..

# 编译
echo_info "编译libcamera..."
meson compile -j$(nproc)

# 安装
echo_info "安装libcamera..."
meson install

# 更新动态链接库缓存
echo_info "更新动态链接库缓存..."
ldconfig

# 清理
echo_info "清理临时文件..."
rm -rf "$BUILD_DIR"

# 安装示例工具（可选）
echo_info "安装额外的工具和示例..."
apt install -y \n    libcamera-tools \n    libcamera-apps

# 完成
echo_success "libcamera库已成功安装！"
echo_info "您可以通过运行 'libcamera-hello' 命令来测试相机是否正常工作"
echo_info "更多信息请访问：https://libcamera.org/"