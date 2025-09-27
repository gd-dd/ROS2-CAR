import subprocess

# 左摄像头的命令
left_cmd = (
    "sudo rpicam-vid --camera 0 --codec mjpeg  -t 0 -o - | "
    "ffmpeg -loglevel quiet -f mjpeg -i - -f mjpeg tcp://127.0.0.1:5000?listen"
)

# 右摄像头的命令
right_cmd = (
    "sudo rpicam-vid --camera 1 --codec mjpeg  -t 0 -o - | "
    "ffmpeg -loglevel quiet -f mjpeg -i - -f mjpeg tcp://127.0.0.1:5001?listen"
)

# 在新的 gnome-terminal 窗口中分别打开每个命令
subprocess.Popen(['gnome-terminal', '--', 'bash', '-c', left_cmd])
subprocess.Popen(['gnome-terminal', '--', 'bash', '-c', right_cmd])

print("两个摄像头的流已在新终端窗口中启动。")
print("现在可以运行你的 Python 预览脚本了。")
