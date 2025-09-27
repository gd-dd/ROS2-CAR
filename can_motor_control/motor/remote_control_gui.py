import sys
import math
import time
import threading
import can
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt5.QtCore import Qt, QPoint, QTimer
from PyQt5.QtGui import QPainter, QColor

# 电机参数
MOTORS = [
    {"id": 0x65, "channel": "can0"},  # 左前
    {"id": 0x66, "channel": "can0"},  # 右前
    {"id": 0x67, "channel": "can1"},  # 右后
    {"id": 0x68, "channel": "can1"},  # 左后
]
station_nos = [0x01, 0x02, 0x03, 0x04]

def speed_frame(station_no, speed_rpm):
    speed_bytes = int(speed_rpm).to_bytes(4, byteorder='little', signed=True)
    return [station_no, 0x20, 0x00, speed_bytes[0], speed_bytes[1], speed_bytes[2], speed_bytes[3], 0xFF]

def send_motor_speeds(buses, speeds):
    for i, motor in enumerate(MOTORS):
        frame = speed_frame(station_nos[i], int(speeds[i]))
        msg = can.Message(arbitration_id=motor["id"], data=frame, is_extended_id=False)
        buses[i].send(msg)

class Joystick(QWidget):
    def __init__(self, label_text, max_radius=80, parent=None):
        super().__init__(parent)
        self.setFixedSize(max_radius*2+10, max_radius*2+30)
        self.max_radius = max_radius
        self.center = QPoint(max_radius+5, max_radius+5)
        self.ball_pos = QPoint(self.center)
        self.pressed = False
        self.label = QLabel(label_text, self)
        self.label.move(0, max_radius*2+5)
        self.value = (0.0, 0.0)  # x, y

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        # Draw outer circle
        painter.setPen(QColor(100,100,100))
        painter.drawEllipse(self.center, self.max_radius, self.max_radius)
        # Draw ball
        painter.setBrush(QColor(50,150,255))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(self.ball_pos, 20, 20)

    def mousePressEvent(self, event):
        if (event.pos()-self.center).manhattanLength() <= self.max_radius+20:
            self.pressed = True
            self.update_ball(event.pos())

    def mouseMoveEvent(self, event):
        if self.pressed:
            self.update_ball(event.pos())

    def mouseReleaseEvent(self, event):
        self.pressed = False
        self.ball_pos = QPoint(self.center)
        self.value = (0.0, 0.0)
        self.update()

    def update_ball(self, pos):
        dx = pos.x() - self.center.x()
        dy = pos.y() - self.center.y()
        r = math.hypot(dx, dy)
        if r > self.max_radius:
            dx = dx * self.max_radius / r
            dy = dy * self.max_radius / r
        self.ball_pos = QPoint(self.center.x() + dx, self.center.y() + dy)
        # 归一化到[-1,1]
        self.value = (dx/self.max_radius, -dy/self.max_radius)
        self.update()

class RemoteControlWindow(QWidget):
    def __init__(self, buses):
        super().__init__()
        self.setWindowTitle("麦克纳姆轮遥控器")
        self.buses = buses

        # 左侧摇杆：万向移动
        self.joystick_move = Joystick("万向移动", max_radius=80)
        # 速度滑条
        self.speed_label = QLabel("速度")
        self.speed_slider = QLabel("0")
        self.speed = 0
        self.speed_max = 5000

        # 右侧摇杆：yaw
        self.joystick_yaw = Joystick("Yaw转向", max_radius=80)

        # 虚拟速度滑条（用鼠标滚轮调节）
        self.joystick_move.setFocusPolicy(Qt.StrongFocus)
        self.joystick_move.wheelEvent = self.wheelEvent_speed

        left_layout = QVBoxLayout()
        left_layout.addWidget(self.joystick_move)
        left_layout.addWidget(self.speed_label)
        left_layout.addWidget(self.speed_slider)

        right_layout = QVBoxLayout()
        right_layout.addWidget(self.joystick_yaw)

        main_layout = QHBoxLayout()
        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)
        self.setLayout(main_layout)

        # 定时刷新
        self.timer = QTimer()
        self.timer.timeout.connect(self.control_loop)
        self.timer.start(50)

        # 使能所有电机
        for i, motor in enumerate(MOTORS):
            frame = [station_nos[i], 0x25, 0x01, 0, 0, 0, 0, 0xFF]
            msg = can.Message(arbitration_id=motor["id"], data=frame, is_extended_id=False)
            self.buses[i].send(msg)

        # 启动心跳线程
        self.heartbeat_running = True
        self.heartbeat_thread = threading.Thread(target=self.heartbeat_loop)
        self.heartbeat_thread.start()

    def wheelEvent_speed(self, event):
        delta = event.angleDelta().y() // 120
        self.speed = max(0, min(self.speed_max, self.speed + delta*100))
        self.speed_slider.setText(str(self.speed))

    def control_loop(self):
        x, y = self.joystick_move.value  # [-1,1]
        speed = self.speed
        yaw, _ = self.joystick_yaw.value  # [-1,1]
        # 车体参数
        L = 80  # 前后长
        W = 60  # 左右宽
        # 菱形麦克纳姆轮速度解算（左前、右前、右后、左后）
        v1 = speed * (y - x + yaw * 1.3)   # 左前
        v2 = speed * (-y - x + yaw * 1.3)  # 右前
        v3 = speed * (-y + x + yaw)  # 右后
        v4 = speed * (y + x + yaw )   # 左后
        speeds = [v1, v2, v3, v4]
        send_motor_speeds(self.buses, speeds)

    def heartbeat_loop(self):
        while self.heartbeat_running:
            for i, motor in enumerate(MOTORS):
                frame = [station_nos[i], 0x08, 0, 0, 0, 0, 0, 0xFF]
                msg = can.Message(arbitration_id=motor["id"], data=frame, is_extended_id=False)
                self.buses[i].send(msg)
            time.sleep(0.1)
            #135792468

    def closeEvent(self, event):
        self.timer.stop()
        self.heartbeat_running = False
        self.heartbeat_thread.join()
        event.accept()

if __name__ == '__main__':
    import os
    os.system("sudo ip link set can0 down")
    os.system("sudo ip link set can0 type can bitrate 1000000")
    os.system("sudo ip link set can0 up")
    os.system("sudo ip link set can1 down")
    os.system("sudo ip link set can1 type can bitrate 1000000")
    os.system("sudo ip link set can1 up")

    bus0 = can.interface.Bus(channel="can0", bustype='socketcan')
    bus1 = can.interface.Bus(channel="can1", bustype='socketcan')
    buses = [bus0, bus0, bus1, bus1]

    app = QApplication(sys.argv)
    win = RemoteControlWindow(buses)
    win.show()
    sys.exit(app.exec_())