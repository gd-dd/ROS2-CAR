# 电机控制模块 (Motor Control)

该目录包含了ROS2-CAR项目中所有与电机控制相关的程序，提供了多种控制方式来操作小车的麦克纳姆轮底盘，实现精准的移动控制。

## 功能概述

本模块主要提供以下功能：
- 基于图形界面的遥控器控制
- WebSocket远程控制
- 电机基本功能测试
- 麦克纳姆轮运动解算
- CAN总线通信与电机控制
- 心跳机制确保通信稳定性

## 目录结构

```
motor/
├── remote_control_gui.py     # 基于PyQt5的图形界面遥控器
├── remote_control_ws_gui.py  # WebSocket远程控制监控界面
└── test_motor_id1.py         # 电机基本功能测试脚本
```

## 核心组件详解

### 1. 图形界面遥控器 (remote_control_gui.py)

该程序实现了一个基于PyQt5的图形界面遥控器，提供直观的摇杆控制方式来操作小车。

**主要功能：**
- 两个自定义摇杆控件：左侧控制万向移动，右侧控制Yaw转向
- 鼠标滚轮调节速度
- 实时显示当前速度值
- 自动初始化CAN总线通信
- 包含心跳机制保持与电机的稳定通信
- 实现麦克纳姆轮的运动解算算法

**使用方法：**

```bash
python remote_control_gui.py
```

**界面说明：**
- 左侧摇杆：控制小车的前后左右移动
- 右侧摇杆：控制小车的转向（Yaw方向）
- 鼠标滚轮：向上滚动增加速度，向下滚动减小速度
- 速度显示：实时显示当前设置的最大速度值

**麦克纳姆轮速度解算原理：**

程序实现了菱形布局麦克纳姆轮的速度解算算法，通过以下公式计算四个轮子的速度：

```python
# 菱形麦克纳姆轮速度解算（左前、右前、右后、左后）
v1 = speed * (y - x + yaw * 1.3)   # 左前
v2 = speed * (-y - x + yaw * 1.3)  # 右前
v3 = speed * (-y + x + yaw)        # 右后
v4 = speed * (y + x + yaw)         # 左后
```

其中：
- `x`：左右移动分量（-1到1）
- `y`：前后移动分量（-1到1）
- `yaw`：转向分量（-1到1）
- `speed`：当前设置的最大速度值
- 1.3是一个比例系数，用于调整转向的灵敏度

### 2. WebSocket远程控制 (remote_control_ws_gui.py)

该程序实现了一个基于WebSocket的远程控制监控界面，能够接收来自WebSocket客户端（如Unity等）的控制指令并控制小车运动。

**主要功能：**
- 使用tkinter实现简单的状态显示界面
- 建立WebSocket客户端连接，接收控制指令
- 自动初始化CAN总线通信
- 包含心跳机制保持与电机的稳定通信
- 实现麦克纳姆轮的运动解算算法

**使用方法：**

```bash
python remote_control_ws_gui.py
```

**配置说明：**

WebSocket服务器地址和端口可在代码中修改：

```python
# WebSocket服务器地址和端口（请根据Unity端实际配置修改）
WS_SERVER = 'ws://localhost:8765'
```

**通信协议：**

程序接收JSON格式的控制指令，包含以下字段：
- `joy`：二维数组 `[x, y]`，表示摇杆的左右和前后分量（-1到1）
- `throttle1`：数值，表示速度控制量
- `throttle2`：数值，表示转向控制量

**麦克纳姆轮速度解算原理：**

```python
# 麦克纳姆轮速度解算\vx, y = self.joy  # [-1,1]
speed = self.throttle1  # 速度
yaw = self.throttle2    # yaw
v1 = speed * (x + y + yaw)
v2 = speed * (x - y - yaw)
v3 = speed * (x - y + yaw)
v4 = speed * (x + y - yaw)
speeds = [v1, v2, v3, v4]
```

### 3. 电机测试脚本 (test_motor_id1.py)

该脚本提供了一个简单的方式来测试电机的基本功能，包括初始化、使能、正转、反转和停止操作。

**主要功能：**
- 自动初始化CAN总线通信
- 使能所有电机
- 依次执行电机的正转、反转和停止操作
- 包含心跳机制确保通信稳定
- 详细的调试信息输出

**使用方法：**

```bash
python test_motor_id1.py
```

**执行流程：**
1. 初始化CAN0和CAN1通道
2. 使能所有四个电机
3. 启动心跳线程
4. 所有电机正转5秒（300RPM）
5. 所有电机反转5秒（-300RPM）
6. 停止所有电机
7. 关闭所有线程和CAN总线

## 电机配置与CAN总线通信

### 电机参数配置

三个程序中都使用了相同的电机参数配置：

```python
MOTORS = [
    {"id": 0x65, "channel": "can0"},  # 左前
    {"id": 0x66, "channel": "can0"},  # 右前
    {"id": 0x67, "channel": "can1"},  # 右后
    {"id": 0x68, "channel": "can1"},  # 左后
]
station_nos = [0x01, 0x02, 0x03, 0x04]  # 对应的站号
```

### CAN总线配置

CAN总线配置参数如下：
- 通道：can0和can1
- 波特率：1000000 bps（1Mbps）
- 通信类型：socketcan

### CAN帧格式说明

程序中使用了几种主要的CAN帧类型：

1. **速度控制帧**：
   ```python
def speed_frame(station_no, speed_rpm):
    speed_bytes = int(speed_rpm).to_bytes(4, byteorder='little', signed=True)
    return [station_no, 0x20, 0x00, speed_bytes[0], speed_bytes[1], speed_bytes[2], speed_bytes[3], 0xFF]
```

2. **使能控制帧**：
   ```python
def enable_frame(station_no, enable=True):
    return [station_no, 0x25, 0x01 if enable else 0x00, 0, 0, 0, 0, 0xFF]
```

3. **停止控制帧**：
   ```python
def stop_frame(station_no):
    return [station_no, 0x26, 0, 0, 0, 0, 0, 0xFF]
```

4. **心跳帧**：
   ```python
frame = [station_no, 0x08, 0, 0, 0, 0, 0, 0xFF]
```

## 心跳机制详解

所有程序都实现了心跳机制，以确保与电机的稳定通信：

```python
def heartbeat_loop(self):
    while self.heartbeat_running:
        for i, motor in enumerate(MOTORS):
            frame = [station_nos[i], 0x08, 0, 0, 0, 0, 0, 0xFF]
            msg = can.Message(arbitration_id=motor["id"], data=frame, is_extended_id=False)
            self.buses[i].send(msg)
        time.sleep(0.1)
```

**心跳机制的作用：**
- 定期向所有电机发送心跳信号，保持通信连接
- 防止电机进入保护模式或停止响应
- 每100毫秒发送一次心跳信号，确保实时性

## 安装与依赖

### 必要的Python库

- `python-can`：用于CAN总线通信
- `PyQt5`：用于图形界面（仅remote_control_gui.py需要）
- `tkinter`：用于简单界面（仅remote_control_ws_gui.py需要）
- `websockets`：用于WebSocket通信（仅remote_control_ws_gui.py需要）
- `asyncio`：用于异步编程（仅remote_control_ws_gui.py需要）

安装依赖库：

```bash
pip install python-can PyQt5 websockets
```

### 系统要求

- 支持SocketCAN的Linux系统
- CAN总线硬件适配器
- 麦克纳姆轮小车底盘
- Python 3.6或更高版本

## 使用指南

### 图形界面遥控器使用步骤

1. 确保CAN总线硬件正确连接
2. 运行程序：`python remote_control_gui.py`
3. 使用鼠标拖动左侧摇杆控制小车前后左右移动
4. 使用鼠标拖动右侧摇杆控制小车转向
5. 使用鼠标滚轮调整速度大小
6. 关闭窗口或按Ctrl+C退出程序

### WebSocket远程控制使用步骤

1. 确保CAN总线硬件正确连接
2. 根据需要修改代码中的WebSocket服务器地址和端口
3. 运行程序：`python remote_control_ws_gui.py`
4. 确保WebSocket客户端（如Unity）已正确配置并连接
5. 通过客户端发送控制指令控制小车
6. 关闭窗口停止程序

### 电机测试使用步骤

1. 确保CAN总线硬件正确连接
2. 运行程序：`python test_motor_id1.py`
3. 观察电机是否按预期执行正转、反转和停止操作
4. 程序会自动在执行完毕后退出

## 常见问题与解决方案

### 1. CAN总线初始化失败

**问题现象**：程序启动时显示"Permission denied"或类似错误

**解决方案**：
- 确保当前用户具有CAN设备的访问权限
- 尝试使用sudo权限运行程序
- 检查CAN总线硬件连接是否正确

### 2. 电机无响应

**问题现象**：程序运行但电机没有任何动作

**解决方案**：
- 检查电机电源连接是否正确
- 确认CAN总线波特率设置是否与电机控制器一致
- 检查电机ID和站号配置是否正确
- 查看程序输出的调试信息，确定是否有数据发送到电机

### 3. WebSocket连接失败

**问题现象**：`remote_control_ws_gui.py`无法连接到WebSocket服务器

**解决方案**：
- 检查WebSocket服务器地址和端口是否正确
- 确保WebSocket服务器正在运行
- 检查网络连接是否正常

## 代码优化建议

1. **错误处理增强**
   - 添加更完善的异常处理机制，提高程序的稳定性
   - 实现CAN总线断开后的自动重连功能

2. **用户体验优化**
   - 为图形界面添加更多状态显示和错误提示
   - 增加速度调节的滑块控件，替代鼠标滚轮

3. **功能扩展**
   - 添加预设动作功能，如自动校准、特定轨迹运动等
   - 实现电机状态监控和反馈显示

4. **性能优化**
   - 优化控制循环的执行效率
   - 考虑使用多线程分离通信和控制逻辑

## 注意事项

1. 所有程序都需要root权限来初始化和操作CAN总线
2. 在未连接实际电机时，建议先使用测试脚本验证CAN通信
3. 调整速度时应从低速开始，逐渐增加到合适的值
4. 长时间不使用时，请关闭程序以避免持续发送心跳信号
5. 详细的CAN电机控制协议请参考项目根目录下的`伺服CAN控制协议及示例V1.1.pdf`文档