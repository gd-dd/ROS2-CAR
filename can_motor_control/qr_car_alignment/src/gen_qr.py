import cv2
import cv2.aruco as aruco

aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_50)
marker_id = 0  # 可选0~49
marker_size = 200  # 像素

img = aruco.drawMarker(aruco_dict, marker_id, marker_size)
cv2.imwrite(f'aruco_{marker_id}.png', img)
print(f'已生成 aruco_{marker_id}.png')