# 摄像头控制模块 (Camera Control)

该目录包含了ROS2-CAR项目中所有与摄像头控制相关的程序，提供了多种方式来预览和管理树莓派摄像头的视频流，为小车的视觉感知和导航提供基础支持。

## 功能概述

本模块主要提供以下功能：
- 单摄像头预览与推流
- 双摄像头同时预览
- 双摄像头TCP流服务
- 官方原生摄像头预览
- 基于PyQt5的图形界面显示

## 目录结构

```
camera/
├── cam0_preview.py          # 单摄像头预览与推流程序
├── dual_camera_preview.py   # 双摄像头PyQt5预览程序
├── dual_camera_stream.py    # 双摄像头TCP流服务程序
└── rpicam_preview.py        # 树莓派原生摄像头预览程序
```

## 核心组件详解

### 1. 单摄像头预览与推流 (cam0_preview.py)

该程序实现了树莓派摄像头0的视频流推流和预览功能，使用rpicam-vid和ffmpeg将视频流推送到本地HTTP端口，并通过OpenCV进行预览显示。

**主要功能：**
- 启动树莓派摄像头0的视频采集
- 使用ffmpeg将视频流推送到本地8080端口（HTTP协议）
- 通过OpenCV读取并显示摄像头流
- 提供按q键退出的交互功能

**使用方法：**

```bash
python cam0_preview.py
```

**实现原理：**

程序首先使用subprocess启动推流命令，等待2秒让推流服务启动，然后使用OpenCV打开HTTP流地址进行显示：

```python
# 启动推流进程
stream_cmd = "sudo rpicam-vid --camera 0 --codec mjpeg -t 0 -o - | ffmpeg -loglevel quiet -f mjpeg -i - -f mjpeg http://127.0.0.1:8080"
proc = subprocess.Popen(stream_cmd, shell=True)
time.sleep(2)  # 等待推流服务启动

# 打开视频流
stream_url = 'http://127.0.0.1:8080'
cap = cv2.VideoCapture(stream_url)
```

### 2. 双摄像头PyQt5预览 (dual_camera_preview.py)

该程序实现了一个基于PyQt5的图形界面应用，用于显示摄像头0的实时画面。程序使用QTimer定时刷新图像，提供流畅的视频预览体验。

**主要功能：**
- 使用PyQt5创建图形界面窗口
- 打开并显示摄像头0的实时画面
- 设置30ms的刷新频率，确保流畅的视频体验
- 窗口关闭时自动释放摄像头资源

**使用方法：**

```bash
python dual_camera_preview.py
```

**技术细节：**

程序使用PyQt5的QTimer实现定时图像刷新，使用QImage和QPixmap在GUI中显示OpenCV读取的图像：

```python
def update_frame(self):
    ret, frame = self.cap.read()
    if ret:
        # OpenCV图像是BGR格式，需要转换为RGB格式以在PyQt5中正确显示
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        img = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
        self.label.setPixmap(QPixmap.fromImage(img))
```

### 3. 双摄像头TCP流服务 (dual_camera_stream.py)

该程序用于同时启动两个摄像头的TCP流服务，将摄像头0和摄像头1的视频流分别推送到本地5000和5001端口，方便其他程序通过TCP协议获取视频流。

**主要功能：**
- 同时启动两个摄像头的视频流服务
- 摄像头0的流发送到本地5000端口（TCP协议）
- 摄像头1的流发送到本地5001端口（TCP协议）
- 在独立的终端窗口中运行每个流服务

**使用方法：**

```bash
python dual_camera_stream.py
```

**流服务启动命令：**

```python
# 左摄像头的命令
left_cmd = (
    "sudo rpicam-vid --camera 0 --codec mjpeg  -t 0 -o - | "
    "ffmpeg -loglevel quiet -f mjpeg -i - -f mjpeg tcp://127.0.0.1:5000?listen"
)

# 右摄像头的命令
right_cmd = (
    "sudo rpicam-vid --camera 1 --codec mjpeg  -t 0 -o - | "
    "ffmpeg -loglevel quiet -f mjpeg -i - -f mjpeg tcp://127.0.0.1:5001?listen"
)
```

### 4. 树莓派原生摄像头预览 (rpicam_preview.py)

该程序使用树莓派官方的rpicam-vid工具直接打开摄像头预览，无需依赖OpenCV和ffmpeg，是一种轻量级的摄像头预览方式。

**主要功能：**
- 使用树莓派官方工具rpicam-vid打开摄像头
- 弹出系统原生的摄像头预览窗口
- 支持设置摄像头分辨率和其他参数

**使用方法：**

```bash
python rpicam_preview.py
```

**预览命令参数：**

```python
cmd = [
    'rpicam-vid',
    '--camera', '0',    # 使用摄像头0
    '--preview',        # 显示预览窗口
    '--codec', 'mjpeg', # 使用MJPEG编码
    '--timeout', '0',   # 无限时长运行
    '--width', '640',   # 图像宽度
    '--height', '480'   # 图像高度
]
```

## 安装与依赖

### 必要的Python库

- `opencv-python`：用于视频流的读取和显示
- `PyQt5`：用于创建图形界面（仅dual_camera_preview.py需要）
- `subprocess`：Python标准库，用于执行系统命令
- `time`：Python标准库，用于时间控制
- `sys`：Python标准库，用于系统交互

安装依赖库：

```bash
pip install opencv-python PyQt5
```

### 系统依赖

- **rpicam-vid**：树莓派官方的摄像头控制工具，适用于Raspberry Pi OS Bullseye及更新版本
- **ffmpeg**：用于视频流的转码和推流
- **gnome-terminal**：用于在新窗口中运行命令（仅dual_camera_stream.py需要）

安装系统依赖：

```bash
sudo apt update
sudo apt install ffmpeg gnome-terminal
```

## 使用指南

### 单摄像头预览

**功能说明**：启动单个摄像头并在OpenCV窗口中显示预览画面

**使用步骤**：
1. 确保摄像头已正确连接到树莓派
2. 打开终端，进入camera目录
3. 运行命令：`python cam0_preview.py`
4. 预览窗口将显示摄像头画面
5. 按q键关闭窗口并退出程序

### 双摄像头TCP流服务

**功能说明**：同时启动两个摄像头的TCP流服务，可被其他程序远程访问

**使用步骤**：
1. 确保两个摄像头都已正确连接到树莓派
2. 打开终端，进入camera目录
3. 运行命令：`python dual_camera_stream.py`
4. 系统将自动打开两个新的终端窗口，分别运行两个摄像头的流服务
5. 其他程序可以通过TCP协议连接到本地5000和5001端口获取视频流
6. 关闭终端窗口可停止流服务

### PyQt5摄像头预览

**功能说明**：使用PyQt5创建的图形界面显示摄像头画面

**使用步骤**：
1. 确保摄像头已正确连接到树莓派
2. 打开终端，进入camera目录
3. 运行命令：`python dual_camera_preview.py`
4. 预览窗口将显示摄像头画面
5. 关闭窗口可退出程序

### 原生摄像头预览

**功能说明**：使用树莓派官方工具直接打开摄像头预览，无需额外依赖

**使用步骤**：
1. 确保摄像头已正确连接到树莓派
2. 打开终端，进入camera目录
3. 运行命令：`python rpicam_preview.py`
4. 系统将弹出树莓派官方的摄像头预览窗口
5. 按Ctrl+C可退出程序

## 常见问题与解决方案

### 1. 摄像头无法打开

**问题现象**：程序报错"无法打开摄像头流"或类似错误

**解决方案**：
- 确认摄像头已正确连接到树莓派
- 检查摄像头是否被其他程序占用
- 验证用户是否有足够的权限访问摄像头设备
- 尝试使用`sudo`权限运行程序

### 2. 预览画面卡顿

**问题现象**：摄像头预览画面不流畅或延迟较大

**解决方案**：
- 降低视频分辨率（修改代码中的width和height参数）
- 增加刷新间隔（修改QTimer的启动参数）
- 关闭其他占用系统资源的程序

### 3. ffmpeg命令执行失败

**问题现象**：程序无法启动ffmpeg推流服务

**解决方案**：
- 确认已正确安装ffmpeg：`sudo apt install ffmpeg`
- 检查系统路径中是否包含ffmpeg
- 尝试使用ffmpeg的完整路径

### 4. rpicam-vid命令不存在

**问题现象**：程序报错找不到rpicam-vid命令

**解决方案**：
- 确认使用的是Raspberry Pi OS Bullseye或更新版本
- 安装libcamera库：`sudo apt install libcamera-apps`

## 代码优化建议

1. **错误处理增强**
   - 添加更完善的异常处理机制
   - 增加摄像头设备状态检测
   - 添加推流服务启动失败的重试机制

2. **功能扩展**
   - 为双摄像头预览程序添加两个摄像头同时显示的功能
   - 增加视频录制功能
   - 添加图像参数调整功能（亮度、对比度等）

3. **性能优化**
   - 优化视频流的读取和显示逻辑
   - 考虑使用多线程分离视频采集和显示

4. **用户体验**
   - 为所有程序添加更友好的GUI界面
   - 增加参数配置界面，避免直接修改代码

## 注意事项

1. 部分程序需要sudo权限才能访问摄像头设备
2. 使用ffmpeg推流会消耗一定的系统资源，请确保树莓派性能足够
3. 长时间运行摄像头会增加功耗和设备温度，请注意散热
4. 在不需要摄像头时，请及时关闭程序以释放系统资源