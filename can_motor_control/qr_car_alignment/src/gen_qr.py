# 导入OpenCV库
import cv2
# 导入OpenCV的ArUco模块，用于生成和检测ArUco标记
import cv2.aruco as aruco

# 创建ArUco字典对象，使用4x4编码格式，最多支持50个标记
aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_50)
# 设置要生成的标记ID，可选范围0~49
marker_id = 0  # 可选0~49
# 设置标记的大小为200像素
marker_size = 200  # 像素

# 根据指定的字典、ID和大小生成ArUco标记图像
img = aruco.drawMarker(aruco_dict, marker_id, marker_size)
# 将生成的标记图像保存为PNG文件
cv2.imwrite(f'aruco_{marker_id}.png', img)
# 打印生成成功的信息
print(f'已生成 aruco_{marker_id}.png')