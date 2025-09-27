import os
import can
import time
import threading

# 自动初始化 CAN 通信
os.system("sudo ip link set can0 down")
os.system("sudo ip link set can0 type can bitrate 1000000")
os.system("sudo ip link set can0 up")
os.system("sudo ip link set can1 down")
os.system("sudo ip link set can1 type can bitrate 1000000")
os.system("sudo ip link set can1 up")

MOTORS = [
    {"id": 0x65, "channel": "can0"},  # 左前
    {"id": 0x66, "channel": "can0"},  # 右前
    {"id": 0x67, "channel": "can1"},  # 右后
    {"id": 0x68, "channel": "can1"},  # 左后
]
station_nos = [0x01, 0x02, 0x03, 0x04]  # 假定站号分别为1,2,3,4

def send_frame(bus, motor_id, data_bytes, desc=""):
    msg = can.Message(arbitration_id=motor_id, data=data_bytes, is_extended_id=False)
    bus.send(msg)
    print(f"[发送] {desc} 电机ID {hex(motor_id)}: {' '.join(f'{b:02X}' for b in data_bytes)}")

def heartbeat(bus, motor_id, station_no, stop_event):
    frame = [station_no, 0x08, 0, 0, 0, 0, 0, 0xFF]
    while not stop_event.is_set():
        send_frame(bus, motor_id, frame, "心跳帧")
        time.sleep(0.1)

def speed_frame(station_no, speed_rpm):
    speed_bytes = int(speed_rpm).to_bytes(4, byteorder='little', signed=True)
    return [station_no, 0x20, 0x00, speed_bytes[0], speed_bytes[1], speed_bytes[2], speed_bytes[3], 0xFF]

def enable_frame(station_no, enable=True):
    return [station_no, 0x25, 0x01 if enable else 0x00, 0, 0, 0, 0, 0xFF]

def stop_frame(station_no):
    return [station_no, 0x26, 0, 0, 0, 0, 0, 0xFF]

if __name__ == '__main__':
    # 打开两个 CAN 通道
    bus0 = can.interface.Bus(channel="can0", bustype='socketcan')
    bus1 = can.interface.Bus(channel="can1", bustype='socketcan')
    buses = [bus0, bus0, bus1, bus1]

    # 使能所有电机
    for i, motor in enumerate(MOTORS):
        send_frame(buses[i], motor["id"], enable_frame(station_nos[i], True), "开启使能")
        time.sleep(0.05)

    # 启动心跳线程
    stop_event = threading.Event()
    threads = []
    for i, motor in enumerate(MOTORS):
        t = threading.Thread(target=heartbeat, args=(buses[i], motor["id"], station_nos[i], stop_event))
        t.start()
        threads.append(t)

    # 正转 5 秒
    for i, motor in enumerate(MOTORS):
        send_frame(buses[i], motor["id"], speed_frame(station_nos[i], 300), "速度模式正转 300rpm")
    print("所有电机正转 5 秒")
    time.sleep(5)

    # 反转 5 秒
    for i, motor in enumerate(MOTORS):
        send_frame(buses[i], motor["id"], speed_frame(station_nos[i], -300), "速度模式反转 -300rpm")
    print("所有电机反转 5 秒")
    time.sleep(5)

    # 停止所有电机
    for i, motor in enumerate(MOTORS):
        send_frame(buses[i], motor["id"], stop_frame(station_nos[i]), "停止")
    print("所有电机停止")

    stop_event.set()
    for t in threads:
        t.join()
    bus0.shutdown()
    bus1.shutdown()