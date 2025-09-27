import cv2

class QRDetector:
    def __init__(self):
        # 初始化二维码检测器
        self.detector = cv2.QRCodeDetector()

    def detect_qr_code(self, frame):
        # 检测二维码并返回内容和中心坐标
        data, points, _ = self.detector.detectAndDecode(frame)
        if points is not None:
            points = points[0]  # 获取二维码四个角点
            center_x = int((points[0][0] + points[2][0]) / 2)
            center_y = int((points[0][1] + points[2][1]) / 2)
            qr_position = (center_x, center_y)
            return data, qr_position
        return None, None