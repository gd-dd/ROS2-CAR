# ROS2工作区说明（Ubuntu版本）

## 工作区结构

此目录已创建为标准的ROS2工作区结构，适用于Ubuntu系统。当前包含以下文件和目录：
- `src/` - 用于存放ROS2包的源代码目录
- `.gitignore` - Git忽略文件，按照ROS2最佳实践配置

## 用途说明

此工作区结构创建在Windows系统上，但设计用于在Ubuntu系统中使用。您可以将此工作区复制到Ubuntu系统后，按照下方说明完成初始化和使用。

## 在Ubuntu上使用步骤

### 1. 安装ROS2

在Ubuntu系统上，您需要先安装ROS2。以Humble Hawksbill版本为例：

```bash
# 设置locale
sudo apt update && sudo apt install locales
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8

# 设置源
sudo apt install software-properties-common
sudo add-apt-repository universe

# 添加ROS2 GPG密钥
sudo apt update && sudo apt install curl
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null

# 安装ROS2
sudo apt update
sudo apt install ros-humble-desktop
sudo apt install ros-dev-tools
```

### 2. 复制工作区到Ubuntu

将此工作区目录复制到您的Ubuntu系统中，例如：
```
/home/your_username/ros2-ws/
```

### 3. 初始化工作区

在Ubuntu系统中打开终端，执行以下步骤：

1. 设置ROS2环境变量：
   ```bash
source /opt/ros/humble/setup.bash
   ```

2. 导航到工作区目录：
   ```bash
cd /path/to/ros2-ws
   ```

3. 运行colcon构建命令：
   ```bash
colcon build
   ```

这将自动创建`build/`、`install/`和`log/`目录，并构建工作区中的所有包。

### 4. 激活工作区

构建完成后，通过以下命令激活工作区：
```bash
source install/local_setup.bash
```

## 在工作区中创建ROS2包

要在工作区中创建新的ROS2包，请按照以下步骤操作：

1. 确保ROS2环境已设置
2. 导航到src目录：
   ```bash
cd src
   ```
3. 使用ros2 pkg create命令创建包，例如：
   ```bash
ros2 pkg create --build-type ament_cmake my_package
   ```

## 工作区管理命令

以下是一些常用的工作区管理命令：

- 只构建特定包：
  ```bash
colcon build --packages-select my_package
  ```

- 清理构建：
  ```bash
rm -rf build/ install/ log/
  ```

- 带符号构建（用于调试）：
  ```bash
colcon build --symlink-install
  ```

## 参考资料
- [ROS2官方文档](https://docs.ros.org/en/humble/)
- [ROS2工作区教程](https://docs.ros.org/en/humble/Tutorials/Beginner-Client-Libraries/Creating-A-Workspace/Creating-A-Workspace.html)
- [ROS2 Ubuntu安装指南](https://docs.ros.org/en/humble/Installation/Ubuntu-Install-Debians.html)