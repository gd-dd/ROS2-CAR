
import os
import sys
import subprocess

# 1. 创建虚拟环境（如未创建）
venv_path = os.path.expanduser('~/venv')
if not os.path.exists(venv_path):
    print('未检测到虚拟环境，正在创建...')
    subprocess.run([sys.executable, '-m', 'venv', venv_path], check=True)

# 2. 激活虚拟环境并安装依赖
def run_in_venv(commands):
    activate = os.path.join(venv_path, 'bin', 'activate')
    shell_cmd = f"source {activate} && {' && '.join(commands)}"
    subprocess.run(shell_cmd, shell=True, check=True, executable='/bin/bash')

required = [
    ('websockets', 'pip install websockets'),
    ('can', 'pip install python-can'),
]
for module, install_cmd in required:
    try:
        __import__(module)
    except ImportError:
        print(f'未检测到 {module}，正在安装...')
        run_in_venv([install_cmd])

# 3. 用虚拟环境运行主程序
activate = os.path.join(venv_path, 'bin', 'activate')
main_py = '/home/jimmy/can_motor_control/motor/remote_control_ws_gui.py'
shell_cmd = f"source {activate} && python {main_py}"
subprocess.run(shell_cmd, shell=True, executable='/bin/bash')
