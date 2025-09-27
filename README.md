# ROS2-CAR 项目

ROS2-CAR是一个基于ROS 2的智能小车控制系统，集成了摄像头视觉、二维码识别和CAN电机控制功能，实现了自动导航和定位。

## 项目结构

```
can_motor_control/
├── .vscode/             # VSCode配置文件
├── camera/              # 相机相关代码
├── motor/               # 电机控制相关代码
├── qr_car_alignment/    # 二维码定位与小车控制
├── run_ws_gui.py        # WebSocket GUI控制脚本
├── src/                 # 源代码目录
└── 伺服CAN控制协议及示例V1.1.pdf  # CAN电机控制协议文档
```

## 主要功能模块

### 1. 二维码定位系统 (qr_car_alignment)

该模块实现了通过摄像头检测二维码并控制小车移动的功能。

**核心组件：**
- `main.py`: 程序入口，负责初始化摄像头、启动QR检测和控制小车运动
- `car_control.py`: 实现CarController类，通过CAN总线控制电机运动
- `qr_detector.py`: 实现QRDetector类，用于检测图像中的二维码
- `utils.py`: 提供图像预处理和坐标转换等工具函数
- `gen_qr.py`: 用于生成ArUco标记的工具脚本

### 2. 相机模块 (camera)

提供了多种相机控制和预览功能，支持单相机和双相机操作。

**主要文件：**
- `cam0_preview.py`: 单相机预览功能
- `dual_camera_preview.py`: 双相机预览功能
- `dual_camera_stream.py`: 双相机流处理
- `rpicam_preview.py`: 树莓派相机预览功能

### 3. 电机控制模块 (motor)

实现了小车电机的控制和远程操作功能。

**主要文件：**
- `remote_control_gui.py`: 远程控制GUI界面
- `remote_control_ws_gui.py`: WebSocket远程控制GUI
- `test_motor_id1.py`: 电机测试脚本

## 系统原理

### 1. 二维码定位原理

系统通过以下步骤实现基于二维码的小车定位和控制：
1. 摄像头捕获环境图像
2. 图像预处理（灰度转换、高斯模糊等）
3. 二维码检测算法识别图像中的二维码
4. 计算二维码中心位置和内容
5. 根据二维码位置和内容控制小车运动
6. 通过TCP协议将检测结果发送到其他系统

### 2. 电机控制原理

小车通过CAN总线控制四个电机（左前、右前、左后、右后），实现前进、后退、左转、右转等运动：
- 使用Python CAN库与CAN总线通信
- 实现了心跳机制确保电机控制稳定
- 支持速度和方向的精确控制

## 快速开始

### 1. 安装依赖

首先安装项目所需的Python库：

```bash
# 安装二维码定位模块依赖
cd can_motor_control/qr_car_alignment
pip install -r requirements.txt

# 安装其他可能需要的依赖
pip install python-can opencv-python websocket-server
```

### 2. 运行二维码定位系统

```bash
cd can_motor_control/qr_car_alignment
python src/main.py
```

### 3. 运行WebSocket远程控制

```bash
cd can_motor_control
python run_ws_gui.py
```

## 技术细节

### CAN总线配置

系统使用两个CAN通道（can0和can1），配置如下：
- 波特率：1000000 bps
- 电机ID：
  - 左前：0x65 (can0)
  - 右前：0x66 (can0)
  - 左后：0x67 (can1)
  - 右后：0x68 (can1)

### 摄像头配置

系统使用libcamera库控制摄像头，主要配置：
- 分辨率：640x480
- 编码格式：MJPEG
- 自动对焦模式：连续
- 目标帧率：30 FPS

## 开发指南

### 1. 添加新的控制算法

如需添加新的控制算法，可以在`qr_car_alignment/src/car_control.py`文件中扩展`CarController`类，实现新的控制方法。

### 2. 改进二维码检测

可以通过以下方法提高二维码检测的准确性：
- 优化图像预处理算法
- 添加更多的检测失败处理机制
- 增加多种二维码格式的支持

### 3. 自定义远程控制界面

可以修改`motor/remote_control_ws_gui.py`文件来自定义远程控制界面的功能和样式。

## 注意事项

1. 运行项目需要管理员权限来配置CAN总线
2. 确保摄像头正确连接并已安装相应驱动
3. 首次运行可能需要调整摄像头参数以获得最佳检测效果
4. 在不同光照条件下可能需要调整图像预处理参数

## 附录

- CAN电机控制协议详见：`伺服CAN控制协议及示例V1.1.pdf`
- 项目使用的二维码为ArUco标记，可以通过`gen_qr.py`生成自定义标记