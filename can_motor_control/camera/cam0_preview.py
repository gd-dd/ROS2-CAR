import cv2
import subprocess
import time

# 先启动推流进程
stream_cmd = "sudo rpicam-vid --camera 0 --codec mjpeg -t 0 -o - | ffmpeg -loglevel quiet -f mjpeg -i - -f mjpeg http://127.0.0.1:8080"
proc = subprocess.Popen(stream_cmd, shell=True)
time.sleep(2)  # 等待推流服务启动

# 打开视频流
stream_url = 'http://127.0.0.1:8080'
cap = cv2.VideoCapture(stream_url)

if not cap.isOpened():
    print('无法打开摄像头流')
    proc.terminate()
    exit()

print('按q键退出')
while True:
    ret, frame = cap.read()
    if ret:
        cv2.imshow('Camera 0', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
proc.terminate()
