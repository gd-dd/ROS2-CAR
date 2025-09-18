#!/usr/bin/env python3

"""
libcamera库安装脚本（Python版本）
适用于Ubuntu系统
此脚本将从源码构建并安装libcamera及其依赖项
"""

import os
import sys
import subprocess
import shutil
import time

# 颜色常量
class Colors:
    INFO = '\033[1;34m'
    SUCCESS = '\033[1;32m'
    ERROR = '\033[1;31m'
    RESET = '\033[0m'

# 函数：打印彩色消息
def print_color(color, message):
    """打印带颜色的消息"""
    print(f"{color}{message}{Colors.RESET}")

# 函数：打印信息消息
def print_info(message):
    """打印信息消息"""
    print_color(Colors.INFO, f"[INFO] {message}")

# 函数：打印成功消息
def print_success(message):
    """打印成功消息"""
    print_color(Colors.SUCCESS, f"[SUCCESS] {message}")

# 函数：打印错误消息
def print_error(message):
    """打印错误消息"""
    print_color(Colors.ERROR, f"[ERROR] {message}")

# 函数：运行系统命令
def run_command(cmd, shell=True, check=True):
    """运行系统命令并返回结果"""
    try:
        subprocess.run(cmd, shell=shell, check=check)
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"命令执行失败: {cmd}")
        print_error(f"错误信息: {e}")
        return False

# 函数：检查是否以root用户运行
def check_root():
    """检查是否以root用户运行"""
    if os.geteuid() != 0:
        print_error("请以root用户运行此脚本（使用sudo）")
        sys.exit(1)

# 主函数
def main():
    """主函数"""
    # 检查是否以root用户运行
    check_root()
    
    # 更新系统包
    print_info("更新系统包...")
    if not run_command("apt update && apt upgrade -y"):
        sys.exit(1)
    
    # 安装必要的依赖项
    print_info("安装构建依赖项...")
    dependencies = [
        "git", "build-essential", "meson", "ninja-build", "pkg-config",
        "libyaml-dev", "python3-yaml", "python3-ply", "python3-jinja2",
        "libgstreamer1.0-dev", "libgstreamer-plugins-base1.0-dev",
        "libgstreamer-plugins-bad1.0-dev", "gstreamer1.0-plugins-base",
        "gstreamer1.0-plugins-good", "gstreamer1.0-plugins-bad",
        "gstreamer1.0-plugins-ugly", "gstreamer1.0-libav", "gstreamer1.0-tools",
        "libudev-dev", "libexif-dev", "libjpeg-dev", "libtiff-dev", "cmake"
    ]
    
    if not run_command(f"apt install -y {' '.join(dependencies)}"):
        sys.exit(1)
    
    # 安装相机特定依赖项（适用于树莓派等平台）
    print_info("安装相机特定依赖项...")
    camera_deps = [
        "libdrm-dev", "libgbm-dev", "libgles2-mesa-dev", "libinput-dev",
        "libudev-dev", "libxkbcommon-dev", "wayland-protocols"
    ]
    
    if not run_command(f"apt install -y {' '.join(camera_deps)}"):
        sys.exit(1)
    
    # 创建临时构建目录
    print_info("创建构建目录...")
    build_dir = f"/tmp/libcamera_build_{int(time.time())}"
    
    # 清理可能存在的旧目录
    if os.path.exists(build_dir):
        try:
            shutil.rmtree(build_dir)
        except Exception as e:
            print_error(f"无法删除旧的构建目录: {e}")
            sys.exit(1)
    
    # 创建新的构建目录
    try:
        os.makedirs(build_dir)
    except Exception as e:
        print_error(f"无法创建构建目录: {e}")
        sys.exit(1)
    
    # 克隆libcamera仓库
    print_info("克隆libcamera仓库...")
    if not run_command(f"git clone https://git.libcamera.org/libcamera/libcamera.git {build_dir}"):
        sys.exit(1)
    
    # 初始化子模块
    print_info("初始化子模块...")
    if not run_command(f"cd {build_dir} && git submodule update --init"):
        sys.exit(1)
    
    # 创建构建目录
    build_subdir = os.path.join(build_dir, "build")
    try:
        os.makedirs(build_subdir)
    except Exception as e:
        print_error(f"无法创建构建子目录: {e}")
        sys.exit(1)
    
    # 配置构建
    print_info("配置libcamera构建...")
    if not run_command(f"cd {build_subdir} && meson setup -Dpipelines=all -Dtest=false -Ddocumentation=false .."):
        sys.exit(1)
    
    # 编译
    print_info("编译libcamera...")
    if not run_command(f"cd {build_subdir} && meson compile -j$(nproc)"):
        sys.exit(1)
    
    # 安装
    print_info("安装libcamera...")
    if not run_command(f"cd {build_subdir} && meson install"):
        sys.exit(1)
    
    # 更新动态链接库缓存
    print_info("更新动态链接库缓存...")
    if not run_command("ldconfig"):
        sys.exit(1)
    
    # 清理
    print_info("清理临时文件...")
    try:
        shutil.rmtree(build_dir)
    except Exception as e:
        print_error(f"清理临时文件时出错: {e}")
        # 这里不退出，因为安装已经完成
    
    # 安装示例工具（可选）
    print_info("安装额外的工具和示例...")
    if not run_command("apt install -y libcamera-tools libcamera-apps"):
        # 这里不退出，因为主要的libcamera已经安装完成
        print_error("示例工具安装失败，但libcamera库已成功安装")
    
    # 完成
    print_success("libcamera库已成功安装！")
    print_info("您可以通过运行 'libcamera-hello' 命令来测试相机是否正常工作")
    print_info("更多信息请访问：https://libcamera.org/")

# 程序入口
if __name__ == "__main__":
    main()