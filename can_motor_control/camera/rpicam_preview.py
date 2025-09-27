import subprocess

# 只用 rpicam-vid 采集并预览摄像头画面
# 直接弹出官方预览窗口，无需OpenCV和ffmpeg

cmd = [
    'rpicam-vid',
    '--camera', '0',
    '--preview',
    '--codec', 'mjpeg',
    '--timeout', '0',  # 无限时长
    '--width', '640',
    '--height', '480'
]

print('正在启动摄像头预览窗口...')
subprocess.run(cmd)


