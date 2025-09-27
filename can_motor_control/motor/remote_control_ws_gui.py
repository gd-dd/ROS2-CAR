
import sys
import math
import time
import threading
import can
import tkinter as tk
import asyncio
import json
import websockets

# 电机参数
MOTORS = [
    {"id": 0x65, "channel": "can0"},  # 左前
    {"id": 0x66, "channel": "can0"},  # 右前
    {"id": 0x67, "channel": "can1"},  # 左后
    {"id": 0x68, "channel": "can1"},  # 右后
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

class RemoteControlWSGUI:
    def __init__(self, root):
        self.root = root
        self.root.title('WebSocket Remote Control Monitor')
        self.joy_label = tk.Label(root, text='Joy: [0, 0]', font=('Arial', 16))
        self.joy_label.pack(pady=10)
        self.throttle1_label = tk.Label(root, text='Throttle1: 0', font=('Arial', 16))
        self.throttle1_label.pack(pady=10)
        self.throttle2_label = tk.Label(root, text='Throttle2: 0', font=('Arial', 16))
        self.throttle2_label.pack(pady=10)
        # 控制数据
        self.joy = [0, 0]
        self.throttle1 = 0
        self.throttle2 = 0
        self.buses = None
        self.heartbeat_running = False

    def update_values(self, joy, throttle1, throttle2):
        self.joy = joy
        self.throttle1 = throttle1
        self.throttle2 = throttle2
        self.joy_label.config(text=f'Joy: {joy}')
        self.throttle1_label.config(text=f'Throttle1: {throttle1}')
        self.throttle2_label.config(text=f'Throttle2: {throttle2}')

    def set_buses(self, buses):
        self.buses = buses
        # 使能所有电机
        for i, motor in enumerate(MOTORS):
            frame = [station_nos[i], 0x25, 0x01, 0, 0, 0, 0, 0xFF]
            msg = can.Message(arbitration_id=motor["id"], data=frame, is_extended_id=False)
            self.buses[i].send(msg)
        # 启动心跳线程
        self.heartbeat_running = True
        self.heartbeat_thread = threading.Thread(target=self.heartbeat_loop)
        self.heartbeat_thread.start()

    def heartbeat_loop(self):
        while self.heartbeat_running:
            for i, motor in enumerate(MOTORS):
                frame = [station_nos[i], 0x08, 0, 0, 0, 0, 0, 0xFF]
                msg = can.Message(arbitration_id=motor["id"], data=frame, is_extended_id=False)
                self.buses[i].send(msg)
            time.sleep(0.1)

    def control_loop(self):
        # 麦克纳姆轮速度解算 - 与remote_control_gui.py保持一致
        x, y = self.joy  # [-1,1]
        speed = self.throttle1  # 速度
        yaw = self.throttle2    # yaw
        # 车体参数 - 与remote_control_gui.py保持一致
        L = 80  # 前后长
        W = 60  # 左右宽
        # 菱形麦克纳姆轮速度解算（左前、右前、右后、左后）
        v1 = speed * (y - x + yaw )   # 左前
        v2 = speed * (-y - x + yaw)  # 右前
        v3 = speed * (-y + x + yaw)  # 右后
        v4 = speed * (y + x + yaw )   # 左后
        speeds = [v1, v2, v3, v4]
        send_motor_speeds(self.buses, speeds)

    def close(self):
        self.heartbeat_running = False
        if hasattr(self, 'heartbeat_thread'):
            self.heartbeat_thread.join()

# WebSocket服务器地址和端口（请根据Unity端实际配置修改）
WS_SERVER = 'ws://localhost:8765'

async def ws_listener(gui):
    print(f"[ws_listener] Connecting to {WS_SERVER}")
    async with websockets.connect(WS_SERVER) as websocket:
        print("[ws_listener] Connected, waiting for messages...")
        while True:
            try:
                msg = await websocket.recv()
                print(f"[ws_listener] Received message: {msg}")
                data = json.loads(msg)
                joy = data.get('joy', [0, 0])
                throttle1 = data.get('throttle1', 0)
                throttle2 = data.get('throttle2', 0)
                print(f"[ws_listener] Parsed joy={joy}, throttle1={throttle1}, throttle2={throttle2}")
                gui.update_values(joy, throttle1, throttle2)
            except Exception as e:
                print('[ws_listener] WebSocket error:', e)
                await asyncio.sleep(1)

def can_init():
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
    return buses

def start_ws(gui):
    asyncio.run(ws_listener(gui))

def periodic_control(gui):
    print("[periodic_control] Control loop started.")
    while True:
        if gui.buses:
            print(f"[periodic_control] Calling control_loop with joy={gui.joy}, throttle1={gui.throttle1}, throttle2={gui.throttle2}")
            gui.control_loop()
        time.sleep(0.05)

if __name__ == '__main__':
    print('启动 remote_control_ws_gui.py')
    root = tk.Tk()
    gui = RemoteControlWSGUI(root)
    print('初始化 CAN 总线...')
    buses = can_init()
    gui.set_buses(buses)
    print('CAN 初始化完成，启动 WebSocket 监听和控制线程...')

    import threading
    def ws_thread():
        print(f'尝试连接 WebSocket: {WS_SERVER}')
        start_ws(gui)
    threading.Thread(target=ws_thread, daemon=True).start()
    threading.Thread(target=periodic_control, args=(gui,), daemon=True).start()

    def on_close():
        print('关闭窗口，停止心跳线程')
        gui.close()
        root.destroy()
    root.protocol("WM_DELETE_WINDOW", on_close)
    print('进入主循环，等待数据...')
    root.mainloop()
