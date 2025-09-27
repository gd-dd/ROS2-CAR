# 导入OpenCV库
import cv2

# 二维码检测器类
class QRDetector:
    # 初始化函数
    def __init__(self):
        # 初始化OpenCV的二维码检测器
        self.detector = cv2.QRCodeDetector()

    # 检测二维码函数
    def detect_qr_code(self, frame):
        # 使用OpenCV的detectAndDecode函数检测二维码，返回数据、角点和二进制掩码
        data, points, _ = self.detector.detectAndDecode(frame)
        # 如果检测到二维码（points不为None）
        if points is not None:
            # 获取二维码的四个角点坐标
            points = points[0]  # 获取二维码四个角点
            # 计算二维码中心的x坐标（取第一个和第三个角点的x坐标平均值）
            center_x = int((points[0][0] + points[2][0]) / 2)
            # 计算二维码中心的y坐标（取第一个和第三个角点的y坐标平均值）
            center_y = int((points[0][1] + points[2][1]) / 2)
            # 构建二维码中心坐标元组
            qr_position = (center_x, center_y)
            # 返回二维码内容和中心坐标
            return data, qr_position
        # 如果未检测到二维码，返回None
        return None, None