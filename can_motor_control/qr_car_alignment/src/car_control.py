# 导入CAN通信库
import can
import math

# 电机参数 - 与remote_control_gui.py保持一致
MOTORS = [
    {"id": 0x65, "channel": "can0"},  # 左前
    {"id": 0x66, "channel": "can0"},  # 右前
    {"id": 0x67, "channel": "can1"},  # 右后
    {"id": 0x68, "channel": "can1"},  # 左后
]
station_nos = [0x01, 0x02, 0x03, 0x04]  # 对应的站号

# 创建速度控制帧的函数 - 与remote_control_gui.py保持一致
def speed_frame(station_no, speed_rpm):
    # 将速度值转换为4字节小端序有符号整数
    speed_bytes = int(speed_rpm).to_bytes(4, byteorder='little', signed=True)
    # 返回完整的速度控制帧数据
    return [station_no, 0x20, 0x00, speed_bytes[0], speed_bytes[1], speed_bytes[2], speed_bytes[3], 0xFF]

# 发送电机速度指令的独立函数 - 与remote_control_gui.py保持一致
def send_motor_speeds(buses, speeds):
    for i, motor in enumerate(MOTORS):
        frame = speed_frame(station_nos[i], int(speeds[i]))
        msg = can.Message(arbitration_id=motor["id"], data=frame, is_extended_id=False)
        buses[i].send(msg)

# 小车控制器类
class CarController:
    # 初始化函数
    def __init__(self):
        # 导入os模块用于执行系统命令
        import os
        # 配置CAN0接口，设置为1Mbps速率 - 与remote_control_gui.py保持一致
        os.system("sudo ip link set can0 down")
        os.system("sudo ip link set can0 type can bitrate 1000000")
        os.system("sudo ip link set can0 up")
        # 配置CAN1接口，设置为1Mbps速率 - 与remote_control_gui.py保持一致
        os.system("sudo ip link set can1 down")
        os.system("sudo ip link set can1 type can bitrate 1000000")
        os.system("sudo ip link set can1 up")
        # 初始化CAN0总线接口
        self.bus0 = can.interface.Bus(channel="can0", bustype='socketcan')
        # 初始化CAN1总线接口
        self.bus1 = can.interface.Bus(channel="can1", bustype='socketcan')
        # 创建总线映射列表，对应四个电机的CAN通道 - 与remote_control_gui.py保持一致
        self.buses = [self.bus0, self.bus0, self.bus1, self.bus1]
        
        # 车体参数 - 与remote_control_gui.py保持一致
        self.L = 80  # 前后长
        self.W = 60  # 左右宽
        self.speed_max = 5000  # 最大速度
        
        # 使能所有电机
        for i, motor in enumerate(MOTORS):
            # 构建使能帧
            frame = [station_nos[i], 0x25, 0x01, 0, 0, 0, 0, 0xFF]
            # 创建CAN消息
            msg = can.Message(arbitration_id=motor["id"], data=frame, is_extended_id=False)
            # 发送CAN消息
            self.buses[i].send(msg)

    # 发送心跳包函数，保持电机连接 - 与remote_control_gui.py保持一致
    def send_heartbeat(self):
        # 为每个电机发送心跳帧
        for i, motor in enumerate(MOTORS):
            # 构建心跳帧
            frame = [station_nos[i], 0x08, 0, 0, 0, 0, 0, 0xFF]
            # 创建CAN消息
            msg = can.Message(arbitration_id=motor["id"], data=frame, is_extended_id=False)
            # 发送CAN消息
            self.buses[i].send(msg)

    # 发送电机速度指令函数
    def send_motor_speeds(self, speeds):
        # 调用与remote_control_gui.py一致的独立函数
        send_motor_speeds(self.buses, speeds)

    # 前进函数
    def move_forward(self, speed):
        # 四个电机都以相同速度正转
        self.send_motor_speeds([speed, speed, speed, speed])

    # 后退函数
    def move_backward(self, speed):
        # 四个电机都以相同速度反转
        self.send_motor_speeds([-speed, -speed, -speed, -speed])

    # 向左平移函数（麦克纳姆轮特性）
    def move_left(self, speed):
        # 左前和右后电机反转，右前和左后电机正转
        self.send_motor_speeds([-speed, speed, speed, -speed])

    # 向右平移函数（麦克纳姆轮特性）
    def move_right(self, speed):
        # 左前和右后电机正转，右前和左后电机反转
        self.send_motor_speeds([speed, -speed, -speed, speed])

    # 停止函数
    def stop(self):
        # 所有电机速度设为0
        self.send_motor_speeds([0, 0, 0, 0])

    # 左转函数 - 基于麦克纳姆轮速度解算算法实现
    def turn_left(self, angle):
        # 将角度转换为速度比例，角度越大，转向速度越快
        # 假设angle范围为0-90度，映射到0-1的比例
        turn_ratio = min(1.0, max(0.0, angle / 90.0))
        # 计算实际转向速度
        turn_speed = self.speed_max * turn_ratio * 0.5  # 转向速度为最大速度的50%
        
        # 左转时，左侧电机反转，右侧电机正转
        v1 = -turn_speed  # 左前
        v2 = turn_speed   # 右前
        v3 = turn_speed   # 右后
        v4 = -turn_speed  # 左后
        
        self.send_motor_speeds([v1, v2, v3, v4])

    # 右转函数 - 基于麦克纳姆轮速度解算算法实现
    def turn_right(self, angle):
        # 将角度转换为速度比例，角度越大，转向速度越快
        # 假设angle范围为0-90度，映射到0-1的比例
        turn_ratio = min(1.0, max(0.0, angle / 90.0))
        # 计算实际转向速度
        turn_speed = self.speed_max * turn_ratio * 0.5  # 转向速度为最大速度的50%
        
        # 右转时，左侧电机正转，右侧电机反转
        v1 = turn_speed   # 左前
        v2 = -turn_speed  # 右前
        v3 = -turn_speed  # 右后
        v4 = turn_speed   # 左后
        
        self.send_motor_speeds([v1, v2, v3, v4])

    # 根据二维码位置对齐小车函数 - 实现基于位置的对齐逻辑
    def align_to_qr(self, qr_position):
        # 假设qr_position是(x, y)坐标，其中(0,0)是图像左上角，(width, height)是图像右下角
        # 获取图像中心位置
        img_center_x = 320  # 假设图像宽度为640像素
        img_center_y = 240  # 假设图像高度为480像素
        
        # 计算二维码中心与图像中心的偏移量
        offset_x = qr_position[0] - img_center_x
        offset_y = qr_position[1] - img_center_y
        
        # 设置对齐阈值，小于此值视为已对齐
        align_threshold = 20  # 像素
        
        # 如果偏移量小于阈值，视为已对齐，停止小车
        if abs(offset_x) < align_threshold and abs(offset_y) < align_threshold:
            self.stop()
            return True  # 返回True表示已对齐
        
        # 根据x方向偏移量进行左右平移对齐
        if abs(offset_x) > align_threshold:
            # 计算平移速度，偏移越大，速度越快，但不超过最大速度的30%
            translate_speed = min(self.speed_max * 0.3, abs(offset_x) * 2)  # 比例系数可调整
            
            if offset_x > 0:
                # 二维码在图像右侧，小车向右平移
                self.move_right(translate_speed)
            else:
                # 二维码在图像左侧，小车向左平移
                self.move_left(translate_speed)
        
        # 根据y方向偏移量进行前后移动对齐
        # 注意：这里可能需要根据实际情况调整，因为y方向的控制可能需要考虑距离
        if abs(offset_y) > align_threshold:
            # 计算移动速度，偏移越大，速度越快，但不超过最大速度的20%
            move_speed = min(self.speed_max * 0.2, abs(offset_y) * 1.5)  # 比例系数可调整
            
            # 如果二维码在图像下方，前进靠近二维码
            # 如果二维码在图像上方，后退远离二维码
            # 注意：这里的逻辑可能需要根据实际摄像头安装位置和视角进行调整
            self.move_forward(move_speed)  # 简单实现，仅向前移动
        
        return False  # 返回False表示未对齐

    # 万向移动函数 - 基于麦克纳姆轮速度解算算法，与remote_control_gui.py保持一致
    def omni_move(self, x, y, yaw, speed=1000):
        # x: 左右移动分量 (-1到1)
        # y: 前后移动分量 (-1到1)
        # yaw: 转向分量 (-1到1)
        # speed: 基础速度值
        
        # 菱形麦克纳姆轮速度解算（左前、右前、右后、左后）
        v1 = speed * (y - x + yaw)
        v2 = speed * (-y - x + yaw)
        v3 = speed * (-y + x + yaw)
        v4 = speed * (y + x + yaw)
        
        self.send_motor_speeds([v1, v2, v3, v4])

    # 关闭CAN总线连接
    def shutdown(self):
        # 停止所有电机
        self.stop()
        # 关闭CAN总线连接
        self.bus0.shutdown()
        self.bus1.shutdown()