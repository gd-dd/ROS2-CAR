import can

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

class CarController:
    def __init__(self):
        import os
        os.system("sudo ip link set can0 down")
        os.system("sudo ip link set can0 type can bitrate 1000000")
        os.system("sudo ip link set can0 up")
        os.system("sudo ip link set can1 down")
        os.system("sudo ip link set can1 type can bitrate 1000000")
        os.system("sudo ip link set can1 up")
        self.bus0 = can.interface.Bus(channel="can0", bustype='socketcan')
        self.bus1 = can.interface.Bus(channel="can1", bustype='socketcan')
        self.buses = [self.bus0, self.bus0, self.bus1, self.bus1]
        # 使能所有电机
        for i, motor in enumerate(MOTORS):
            frame = [station_nos[i], 0x25, 0x01, 0, 0, 0, 0, 0xFF]
            msg = can.Message(arbitration_id=motor["id"], data=frame, is_extended_id=False)
            self.buses[i].send(msg)

    def send_heartbeat(self):
        for i, motor in enumerate(MOTORS):
            frame = [station_nos[i], 0x08, 0, 0, 0, 0, 0, 0xFF]
            msg = can.Message(arbitration_id=motor["id"], data=frame, is_extended_id=False)
            self.buses[i].send(msg)

    def send_motor_speeds(self, speeds):
        for i, motor in enumerate(MOTORS):
            frame = speed_frame(station_nos[i], int(speeds[i]))
            msg = can.Message(arbitration_id=motor["id"], data=frame, is_extended_id=False)
            self.buses[i].send(msg)

    def move_forward(self, speed):
        self.send_motor_speeds([speed, speed, speed, speed])

    def move_backward(self, speed):
        self.send_motor_speeds([-speed, -speed, -speed, -speed])

    def move_left(self, speed):
        self.send_motor_speeds([-speed, speed, speed, -speed])

    def move_right(self, speed):
        self.send_motor_speeds([speed, -speed, -speed, speed])

    def stop(self):
        self.send_motor_speeds([0, 0, 0, 0])

    def turn_left(self, angle):
        # Code to turn the car left by the specified angle
        pass

    def turn_right(self, angle):
        # Code to turn the car right by the specified angle
        pass

    def align_to_qr(self, qr_position):
        # Code to align the car based on the QR code position
        # This could involve moving forward, backward, or turning
        pass