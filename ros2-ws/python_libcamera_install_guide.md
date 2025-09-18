# libcamera库Python安装指南

## 关于此Python脚本

`install_libcamera.py`是`install_libcamera.sh`的Python版本，用于在Ubuntu系统上从源码构建并安装libcamera库及其依赖项。两个脚本功能相同，但实现方式不同。

## 使用方法

在Ubuntu系统上，按照以下步骤运行Python脚本：

1. 将此脚本复制到Ubuntu系统中

2. 打开终端，导航到脚本所在目录

3. 赋予脚本执行权限：
   ```bash
   chmod +x install_libcamera.py
   ```

4. 以root权限运行脚本：
   ```bash
   sudo python3 install_libcamera.py
   ```
   或者直接：
   ```bash
   sudo ./install_libcamera.py
   ```

## Python脚本的优势

与bash脚本相比，Python脚本具有以下优势：

1. **更好的错误处理** - Python提供了更强大的异常处理机制
2. **更清晰的代码结构** - 使用函数和类组织代码，易于维护和扩展
3. **更灵活的逻辑控制** - 可以实现更复杂的安装逻辑
4. **更好的跨平台兼容性** - 虽然主要为Ubuntu设计，但Python代码更容易适配其他系统

## 脚本功能

此Python脚本将自动执行以下操作：

- 更新系统包
- 安装所有必要的构建依赖项
- 从官方仓库克隆libcamera源代码
- 初始化子模块
- 配置、编译和安装libcamera
- 更新动态链接库缓存
- 安装额外的工具和示例应用程序
- 提供详细的进度和错误信息

## 验证安装

安装完成后，您可以通过运行以下命令来验证libcamera是否成功安装：
```bash
libcamera-hello
```

如果相机正常工作，您将看到相机捕获的实时图像。

## 支持的Ubuntu版本

此脚本已在以下Ubuntu版本上测试：
- Ubuntu 22.04 LTS
- Ubuntu 20.04 LTS

## 注意事项

- 脚本需要以root权限运行
- 安装过程可能需要较长时间，具体取决于您的网络速度和系统性能
- 如果遇到依赖项问题，脚本会显示详细的错误信息
- 安装完成后，脚本会自动清理临时文件
- 确保系统已安装Python 3（Ubuntu默认已安装）

## 故障排除

如果安装失败，请检查以下几点：

1. 确保您的Ubuntu系统已连接到互联网
2. 确保您有足够的磁盘空间（至少需要2GB）
3. 尝试手动安装失败的依赖项，然后重新运行脚本
4. 查看脚本输出的错误信息，针对性地解决问题

## 更多信息

- [libcamera官方网站](https://libcamera.org/)
- [libcamera GitHub仓库](https://github.com/libcamera-org/libcamera)