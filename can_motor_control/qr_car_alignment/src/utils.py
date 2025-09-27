import cv2
import math

def preprocess_image(image):
    # 将图像转换为灰度并进行高斯模糊预处理
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    return blurred

def convert_coordinates(qr_position, image_shape):
    # 将归一化的二维码位置转换为图像坐标
    height, width = image_shape[:2]
    x_center = qr_position[0] * width
    y_center = qr_position[1] * height
    return (x_center, y_center)

def calculate_distance_to_qr(qr_position, car_position):
    # 计算二维码与小车之间的欧氏距离
    return math.sqrt((qr_position[0] - car_position[0]) ** 2 + (qr_position[1] - car_position[1]) ** 2)

def adjust_speed(distance):
    # 根据距离调整小车速度
    if distance < 50:
        return 0  # 停止
    elif distance < 100:
        return 0.5  # 减速
    else:
        return 1.0  # 全速