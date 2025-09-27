# QR Car Alignment Project

This project implements an automated car alignment system using QR code detection. The car will adjust its position based on the detected QR codes in the environment.

## Installation Instructions

1. Install dependencies:
   Run the following command in the project root directory to install the required libraries:
   ```
   pip install -r requirements.txt
   ```

2. Run the program:
   Use the following command to start the program:
   ```
   python src/main.py
   ```

## Project Structure

- `src/main.py`: The entry point of the program. It initializes the camera, calls the QR detector, and controls the car's movement based on the detected QR code position.
  
- `src/car_control.py`: Contains the `CarController` class, which controls the car's movement. It provides methods to move forward, move backward, turn left, and turn right to adjust the car's direction and speed based on the QR code's position.

- `src/qr_detector.py`: Contains the `QRDetector` class, which uses OpenCV to detect QR codes in the images captured by the camera. It provides a method to detect QR codes and return their positions and data.

- `src/utils.py`: Contains utility functions, such as image processing and coordinate transformation helpers.

- `requirements.txt`: Lists the required Python libraries for the project, including `opencv-python` and `pyzbar` for QR code detection.

## Example Script

Here is an example code snippet for `src/main.py`:

```python
import cv2
from car_control import CarController
from qr_detector import QRDetector

def main():
    car = CarController()
    qr_detector = QRDetector()
    
    cap = cv2.VideoCapture(0)  # Open the camera

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        qr_data, qr_position = qr_detector.detect_qr_code(frame)
        
        if qr_data:
            # Control the car based on QR code position
            car.align_to_qr(qr_position)
        
        cv2.imshow("Camera", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
```

## Model Training Methods

To improve the accuracy of QR code detection, consider the following methods:

1. **Data Collection**: Gather QR code images under various environmental and lighting conditions.
2. **Data Augmentation**: Use image processing techniques (such as rotation, scaling, flipping, etc.) to enhance the dataset.
3. **Model Selection**: Choose an appropriate deep learning model (like YOLO, SSD, etc.) for training.
4. **Training**: Train the model using the collected data, adjusting hyperparameters to optimize performance.
5. **Evaluation**: Assess the model's accuracy on a test set and make necessary adjustments.

By following these steps, you can train a QR code detection model suitable for specific environments.