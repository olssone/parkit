import cv2
import numpy as np
import time
from yolov5 import YOLOv5  # Import the YOLOv5 package

# Load a pre-trained YOLOv5 model
yolov5_model = YOLOv5("yolov5s.pt", device="cpu")  # You can choose from yolov5s, yolov5m, yolov5l, yolov5x

# Rectangle parameters: [x, y, width, height]
rect = [200, 200, 500, 225]  # Initial position and size (width > height)
reference_frame = None
occupied_start_time = None
confirmed_occupied = False
move_dist = 5  # Distance to move the rectangle per key press

# Function to check if the box is occupied
def check_occupation(frame, rect, reference_frame):
    global occupied_start_time, confirmed_occupied

    x, y, w, h = rect
    roi = frame[y:y+h, x:x+w]
    if reference_frame is not None:
        diff = cv2.absdiff(roi, reference_frame)
        gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 25, 255, cv2.THRESH_BINARY)
        count = cv2.countNonZero(thresh)

        occupied = count > (w * h * 0.1)  # Threshold, adjust as needed

        if occupied:
            if occupied_start_time is None:
                occupied_start_time = time.time()
        else:
            occupied_start_time = None
            confirmed_occupied = False

        return occupied, reference_frame

    return False, reference_frame

# Capture video from the webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read frame from webcam.")
        break

    # Update the reference frame
    if reference_frame is None:
        x, y, w, h = rect
        reference_frame = frame[y:y+h, x:x+w].copy()

    # Draw the rectangle and the dot
    cv2.rectangle(frame, (rect[0], rect[1]), (rect[0]+rect[2], rect[1]+rect[3]), (0, 255, 0), 2)
    center = (rect[0] + rect[2] // 2, rect[1] + rect[3] // 2)
    dot_color = (0, 0, 255) if confirmed_occupied else (0, 255, 0)
    cv2.circle(frame, center, 10, dot_color, -1)

    # Check if the space is occupied
    occupied, _ = check_occupation(frame, rect, reference_frame)

    if occupied and occupied_start_time:
        if time.time() - occupied_start_time > 10:
            msg = "SPACE OCCUPIED"
            print(msg)
            cv2.putText(frame, msg, (rect[0], rect[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
            confirmed_occupied = True
            
            # Object detection with YOLOv5
            roi = frame[rect[1]:rect[1]+rect[3], rect[0]:rect[0]+rect[2]]
            results = yolov5_model.predict(roi)
            
            # Convert the results to a Pandas DataFrame
            predictions_df = results.pandas().xyxy[0]  # The first element is for the first image in the batch

            # Filter predictions for 'car' detections
            car_detections = predictions_df[predictions_df['name'] == 'car']

            # Iterate through each car detection
            for index, row in car_detections.iterrows():
                # Extract bounding box coordinates, confidence score, and class name
                class_name = row['name']  # This will be 'car' for all rows in car_detections
                if class_name == "car":
                    # Now, you can use xmin, ymin, xmax, ymax, confidence, and class_name as needed
                    car_msg = "CAR IN SPACE"
                    print(car_msg)
                    cv2.putText(frame, car_msg, (rect[0], rect[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 2)

            
            # Draw rectangles around detected objects on the original frame
            for result in results.xyxy[0]:  # xyxy is for [xmin, ymin, xmax, ymax, confidence, class]
                xmin, ymin, xmax, ymax = map(int, result[:4])
                cv2.rectangle(frame, (xmin+rect[0], ymin+rect[1]), (xmax+rect[0], ymax+rect[1]), (255, 0, 0), 2)



    cv2.imshow('frame', frame)

    # Move the rectangle based on key presses
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('w'):  # Move up
        rect[1] -= move_dist
    elif key == ord('s'):  # Move down
        rect[1] += move_dist
    elif key == ord('a'):  # Move left
        rect[0] -= move_dist
    elif key == ord('d'):  # Move right
        rect[0] += move_dist
    elif key == ord('r'):  # Reset reference frame
        reference_frame = None
        confirmed_occupied = False

cap.release()
cv2.destroyAllWindows()