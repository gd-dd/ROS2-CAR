# 导入OpenCV库，用于图像处理和显示
import cv2
# 导入time库，用于时间控制和延时
import time
# 导入threading库，用于创建和管理线程
import threading
# 导入CarController类，用于控制小车的运动
from car_control import CarController
# 导入preprocess_image函数，用于图像预处理
from utils import preprocess_image
# 导入socket库，用于TCP通信
import socket
# 导入LED控制相关函数
from led_control import init_led_strips, turn_on_leds, turn_off_leds, cleanup

# 心跳循环函数，用于定期向电机发送心跳信号
# 参数: controller - CarController实例，用于发送心跳
def heartbeat_loop(controller):
    # 无限循环发送心跳信号
    while True:
        # 调用控制器的发送心跳方法
        controller.send_heartbeat()
        # 每100毫秒发送一次心跳
        time.sleep(0.1)

# 主函数，程序的入口点
def main():
    # 初始化小车控制器 - 与remote_control_gui.py保持一致的参数配置
    controller = CarController()
    # 启动心跳线程，确保电机通信稳定
    # daemon=True表示主线程结束时，心跳线程也会自动结束
    threading.Thread(target=heartbeat_loop, args=(controller,), daemon=True).start()
    
    # 初始化LED灯条
    print("初始化LED灯条...")
    strip_white, strip_red = init_led_strips()
    # 打开LED灯
    turn_on_leds(strip_white, strip_red)
    print("LED灯已打开")

    # 导入subprocess和signal库，用于启动和控制外部进程
    import subprocess
    import signal
    # 打印启动摄像头流的信息
    print("Starting camera stream...")
    # 启动libcamera-vid进程，捕获摄像头图像并保存到共享内存
    cam_proc = subprocess.Popen([
        "sudo", "libcamera-vid",         # 使用sudo权限运行libcamera-vid命令
        "-t", "0",                       # 设置超时时间为无限（持续运行）
        "--width", "640", "--height", "480", # 设置图像分辨率为640x480
        "--codec", "mjpeg",               # 使用MJPEG编码格式
        "--autofocus-mode", "continuous", # 设置自动对焦模式为连续
        "--inline",                        # 内联MJPEG帧头
        "-o", "/dev/shm/cam.mjpeg"         # 将输出保存到共享内存文件
    ])
    # 等待0秒，让摄像头有时间初始化
    time.sleep(1)

    # 使用OpenCV打开共享内存中的摄像头流
    cap = cv2.VideoCapture('/dev/shm/cam.mjpeg')
    # 创建二维码检测器实例
    qr_detector = cv2.QRCodeDetector()

    # 初始化TCP客户端，用于发送检测到的二维码信息
    tcp_host = '127.0.0.1'  # TCP服务器地址（本地主机）
    tcp_port = 9000         # TCP服务器端口
    # 创建TCP套接字
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # 尝试连接到TCP服务器
        sock.connect((tcp_host, tcp_port))
        # 打印连接成功信息
        print(f"Connected to TCP server {tcp_host}:{tcp_port}")
    except Exception as e:
        # 打印连接失败信息
        print(f"TCP连接失败: {e}")
        # 设置sock为None，表示连接失败
        sock = None

    # 打印运行信息和退出提示
    print("Running. Press Ctrl+C or q to exit.")

    # 初始化状态文本
    status_text = ""
    # 设置窗口名称
    window_name = "QR Detector"
    # 创建OpenCV窗口，WINDOW_NORMAL表示可以调整窗口大小
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    # 设置目标帧率为30fps
    target_fps = 30  # 目标帧率
    # 计算每帧之间的时间间隔
    frame_interval = 1 / target_fps
    # 记录开始时间，用于计算帧率
    start_time = time.time()
    # 目标帧数，理论上应该达到的帧数
    logical_frame = 50  # 目标帧数
    # 当前实际处理的帧数
    current_frame = 0  # 当前帧数
    # 上次跳过的帧数
    last_jump = 0      # 上次跳过帧数

    try:
        # 初始化计数器
        count = 0
        # 主循环，持续处理图像
        while True:
            # 获取当前时间
            now = time.time()
            # 计算当前应该处理到的目标帧数
            logical_frame = int((now - start_time) * target_fps)
            # 计算当前帧数与目标帧数的差值
            # 根据差值实现更陡峭的跳帧策略，保证程序运行流畅
            # 如果落后帧数>6跳3帧，>3跳2帧，>1跳1帧，否则不跳
            diff = logical_frame - current_frame
            if diff > 6:
                jump = 3
            elif diff > 3:
                jump = 2
            elif diff > 1:
                jump = 1
            else:
                jump = 0

            # 执行跳帧处理，只抓取图像而不进行解码和处理
            for _ in range(jump):
                cap.grab()
                current_frame += 1

            # 读取并解码一帧图像
            ret, frame = cap.read()
            current_frame += 1

            # 检查图像读取是否成功
            if not ret or frame is None:
                status_text = "Camera read failed, retrying..."
                print(status_text, end=' ')
                # 如果读取失败，等待1秒后重试
                time.sleep(1)
                continue

            # 获取图像的高度和宽度
            h, w = frame.shape[:2]

            # 对图像进行预处理，提高二维码检测效果
            processed = preprocess_image(frame)

            # 使用OpenCV的QRCodeDetector进行二维码检测和解码
            # data: 解码后的二维码内容
            # bbox: 二维码的边界框坐标
            data, bbox, _ = qr_detector.detectAndDecode(processed)
            # 检查是否检测到有效的二维码
            if bbox is not None and data:
                # 将边界框坐标转换为整数
                pts = bbox[0].astype(int)
                # 在图像上绘制二维码边界框
                for i in range(4):
                    cv2.line(frame, tuple(pts[i]), tuple(pts[(i+1)%4]), (0,255,0), 2)
                # 更新状态文本，显示解码后的内容
                status_text = f"QR Content: {data}"
                # 如果TCP连接存在，发送二维码内容
                if sock:
                    try:
                        sock.sendall(data.encode('utf-8'))
                    except Exception as e:
                        print(f"TCP发送失败: {e}", end=' ')
                        # 发送失败后，将sock设为None
                        sock = None
                # 检测到二维码时，控制小车前进
                # 使用与remote_control_gui.py一致的速度值
                controller.move_forward(500)
            else:
                # 未检测到二维码时，更新状态文本
                status_text = "QR code not detected"
                # 未检测到二维码时，控制小车停止
                controller.stop()

            # 增加计数器
            count += 1

            # 在控制台打印当前处理状态信息（不换行，覆盖上一行）
            print(f"\rCurrent:{current_frame} Target:{logical_frame} Jumped:{jump} Result:{status_text}", end='')

            # 在图像上显示状态文本
            cv2.putText(frame, status_text, (10, h-10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)
            # 显示处理后的图像
            cv2.imshow(window_name, frame)
            # 等待1毫秒，如果用户按下'q'键则退出循环
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            # 帧率控制：如果当前帧已经赶上或超过目标帧，则延时等待
            now2 = time.time()
            logical_frame2 = int((now2 - start_time) * target_fps)
            # 如果当前帧还未赶上目标帧，则继续处理下一帧
            if current_frame < logical_frame2:
                continue
            # 计算需要休眠的时间，以保持目标帧率
            sleep_time = start_time + (current_frame) * frame_interval - time.time()
            # 如果需要休眠的时间大于0，则执行休眠
            if sleep_time > 0:
                time.sleep(sleep_time)
    finally:
        # 释放摄像头资源
        cap.release()
        # 关闭所有OpenCV窗口
        cv2.destroyAllWindows()
        # 向摄像头进程发送中断信号，停止摄像头
        cam_proc.send_signal(signal.SIGINT)
        # 如果TCP套接字存在，则关闭连接
        if sock:
            sock.close()
        # 关闭CAN总线连接，确保资源正确释放
        controller.shutdown()
        # 关闭LED灯并清理资源
        print("正在关闭LED灯...")
        turn_off_leds(strip_white, strip_red)
        cleanup()
        print("LED灯已关闭")

# 如果直接运行此脚本，则执行main函数
if __name__ == "__main__":
    main()