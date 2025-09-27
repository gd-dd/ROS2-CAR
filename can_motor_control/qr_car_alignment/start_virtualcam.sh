#!/bin/bash
# 一键启动虚拟摄像头和识别脚本

set -e

# 启动v4l2loopback虚拟摄像头（如已启动可跳过）
sudo modprobe v4l2loopback video_nr=10 card_label="virtualcam" exclusive_caps=1 || true

# 启动libcamera-vid推流到虚拟摄像头
sudo pkill libcamera-vid || true
sudo libcamera-vid -t 0 --width 640 --height 480 --codec yuv420 --autofocus-mode continuous -o /dev/video10 &

sleep 2

# 启动python识别脚本
python3 /home/jimmy/can_motor_control/qr_car_alignment/src/main.py
