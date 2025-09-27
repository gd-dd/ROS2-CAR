# 导入OpenCV库用于图像处理
import cv2
# 导入math库用于数学计算
import math

# 图像预处理函数
def preprocess_image(image):
    # 将彩色图像转换为灰度图像
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # 对灰度图像进行高斯模糊处理，使用5x5的卷积核，标准差为0
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    # 返回预处理后的图像
    return blurred

# 坐标转换函数
def convert_coordinates(qr_position, image_shape):
    # 从图像形状获取高度和宽度
    height, width = image_shape[:2]
    # 将归一化的x坐标转换为实际像素坐标
    x_center = qr_position[0] * width
    # 将归一化的y坐标转换为实际像素坐标
    y_center = qr_position[1] * height
    # 返回转换后的坐标元组
    return (x_center, y_center)

# 计算二维码与小车之间距离的函数
def calculate_distance_to_qr(qr_position, car_position):
    # 使用欧氏距离公式计算两个点之间的距离
    return math.sqrt((qr_position[0] - car_position[0]) ** 2 + (qr_position[1] - car_position[1]) ** 2)

# 根据距离调整小车速度的函数
def adjust_speed(distance):
    # 如果距离小于50个单位，返回0表示停止
    if distance < 50:
        return 0  # 停止
    # 如果距离在50到100个单位之间，返回0.5表示减速
    elif distance < 100:
        return 0.5  # 减速
    # 如果距离大于等于100个单位，返回1.0表示全速
    else:
        return 1.0  # 全速