# ROS2工作区说明

## 工作区结构

此目录已创建为标准的ROS2工作区。当前包含以下结构：
- `src/` - 用于存放ROS2包的源代码目录

## 重要提示

在使用此工作区之前，您需要先**安装ROS2并配置环境**。目前系统中未检测到ROS2环境。

## 安装ROS2的步骤

1. 访问ROS2官方网站下载适合Windows的ROS2发行版：https://docs.ros.org/en/humble/Installation/Windows-Install-Binary.html
2. 按照官方文档完成安装
3. 安装完成后，通过运行以下命令设置环境变量：
   ```
   call C:\path\to\ros2\install\local_setup.bat
   ```

## 初始化工作区

安装并配置ROS2后，您可以通过以下步骤初始化工作区：

1. 打开命令提示符
2. 设置ROS2环境变量
3. 导航到工作区目录
4. 运行colcon构建命令：
   ```
   colcon build
   ```

这将自动创建`build/`、`install/`和`log/`目录，并构建工作区中的所有包。

## 激活工作区

构建完成后，通过以下命令激活工作区：
```
call install\local_setup.bat
```

## 参考资料
- [ROS2官方文档](https://docs.ros.org/en/humble/)
- [ROS2工作区教程](https://docs.ros.org/en/humble/Tutorials/Beginner-Client-Libraries/Creating-A-Workspace/Creating-A-Workspace.html)