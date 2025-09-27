import cv2
import time
import threading
from car_control import CarController
from utils import preprocess_image
import socket

def heartbeat_loop(controller):
    while True:
        controller.send_heartbeat()
        time.sleep(0.1)

def main():
    # 初始化小车控制器
    controller = CarController()
    # 启动心跳线程
    threading.Thread(target=heartbeat_loop, args=(controller,), daemon=True).start()

    import subprocess
    import signal
    print("Starting camera stream...")
    cam_proc = subprocess.Popen([
        "sudo", "libcamera-vid", "-t", "0", "--width", "640", "--height", "480", "--codec", "mjpeg",
        "--autofocus-mode", "continuous", "--inline", "-o", "/dev/shm/cam.mjpeg"
    ])
    time.sleep(0.5)  # Give camera time to initialize

    cap = cv2.VideoCapture('/dev/shm/cam.mjpeg')
    qr_detector = cv2.QRCodeDetector()

    # 初始化TCP客户端
    tcp_host = '127.0.0.1'
    tcp_port = 9000
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((tcp_host, tcp_port))
        print(f"Connected to TCP server {tcp_host}:{tcp_port}")
    except Exception as e:
        print(f"TCP连接失败: {e}")
        sock = None

    print("Running. Press Ctrl+C or q to exit.")

    status_text = ""
    window_name = "QR Detector"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    target_fps = 30  # 目标帧率
    frame_interval = 1 / target_fps
    start_time = time.time()
    logical_frame = 0  # 目标帧数
    current_frame = 0  # 当前帧数
    last_jump = 0      # 上次跳过帧数

    try:
        count = 0
        while True:
            now = time.time()
            logical_frame = int((now - start_time) * target_fps)
            # 更陡峭的跳帧曲线：如果落后帧数>6跳3帧，>3跳2帧，>1跳1帧，否则不跳
            diff = logical_frame - current_frame
            if diff > 6:
                jump = 3
            elif diff > 3:
                jump = 2
            elif diff > 1:
                jump = 1
            else:
                jump = 0

            # 跳帧处理
            for _ in range(jump):
                cap.grab()
                current_frame += 1

            ret, frame = cap.read()
            current_frame += 1

            if not ret or frame is None:
                status_text = "Camera read failed, retrying..."
                print(status_text, end=' ')
                time.sleep(1)
                continue

            h, w = frame.shape[:2]

            # 图像预处理
            processed = preprocess_image(frame)

            # 二维码检测
            data, bbox, _ = qr_detector.detectAndDecode(processed)
            if bbox is not None and data:
                pts = bbox[0].astype(int)
                for i in range(4):
                    cv2.line(frame, tuple(pts[i]), tuple(pts[(i+1)%4]), (0,255,0), 2)
                status_text = f"QR Content: {data}"
                # 检测到二维码时通过TCP发送内容
                if sock:
                    try:
                        sock.sendall(data.encode('utf-8'))
                    except Exception as e:
                        print(f"TCP发送失败: {e}", end=' ')
                        sock = None
                # 检测到二维码则前进
                controller.move_forward(500)
            else:
                status_text = "QR code not detected"
                # 未检测到二维码则静止
                controller.stop()

            count += 1

            # 打印当前帧、目标帧、跳过帧数、识别结果（不换行）
            print(f"\rCurrent:{current_frame} Target:{logical_frame} Jumped:{jump} Result:{status_text}", end='')

            cv2.putText(frame, status_text, (10, h-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)
            cv2.imshow(window_name, frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            # 如果当前帧已经赶上或超过目标帧，则延时
            now2 = time.time()
            logical_frame2 = int((now2 - start_time) * target_fps)
            if current_frame < logical_frame2:
                continue
            sleep_time = start_time + (current_frame) * frame_interval - time.time()
            if sleep_time > 0:
                time.sleep(sleep_time)
    finally:
        cap.release()
        cv2.destroyAllWindows()
        cam_proc.send_signal(signal.SIGINT)
        if sock:
            sock.close()

if __name__ == "__main__":
    main()