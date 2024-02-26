import cv2
import numpy as np
import time
import torch
from PIL import Image

# Rectangle parameters: [x, y, width, height]
rect = [775, 550, 500, 225]  # Initial position and size (width > height)
reference_frame = None
occupied_start_time = None
confirmed_occupied = False
detection_attempts = 0  # Counter for detection attempts
car_detected = False  # Flag to indicate if a car is detected
move_dist = 5  # Distance to move the rectangle per key press

# Function to check if the box is occupied
def check_occupation(frame, rect, reference_frame):
    global occupied_start_time, confirmed_occupied, detection_attempts, car_detected

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
            if occupied_start_time is not None:
                # Space just became unoccupied, reset everything for a new cycle
                reset_state()
            occupied_start_time = None

        return occupied, reference_frame

    return False, reference_frame

def reset_state():
    global reference_frame, occupied_start_time, confirmed_occupied, detection_attempts, car_detected
    reference_frame = None
    occupied_start_time = None
    confirmed_occupied = False
    car_detected = False

def load_image_from_array(image_array):
    # Convert the image array (OpenCV format) to a PIL Image
    return Image.fromarray(cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB))

def detect_objects(image):
    # Load the YOLOv5 model
    model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)

    # Perform inference
    results = model(image)

    # Extract class indices of detected objects
    class_indices = results.xyxy[0][:, -1].int().tolist()  # Convert tensor indices to a list of integers

    # Map indices to their corresponding class names
    detected_objects = [results.names[i] for i in class_indices]

    return detected_objects

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

    # Draw the rectangle
    cv2.rectangle(frame, (rect[0], rect[1]), (rect[0]+rect[2], rect[1]+rect[3]), (0, 255, 0), 2)

    # Check if the space is occupied
    occupied, _ = check_occupation(frame, rect, reference_frame)

    if occupied and not confirmed_occupied:
        if time.time() - occupied_start_time > 10:  # Wait for 10 seconds to confirm the object is stationary
            confirmed_occupied = True
            if not car_detected:
                roi = frame[rect[1]:rect[1]+rect[3], rect[0]:rect[0]+rect[2]]
                pil_image = load_image_from_array(roi)
                detected_objects = detect_objects(pil_image)
                if "car" in detected_objects:
                    car_detected = True


    if confirmed_occupied:
        if car_detected:
            cv2.putText(frame, "Car is parked", (frame.shape[1] - 200, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        elif detection_attempts >= 3:
            cv2.putText(frame, "Car is not parked", (frame.shape[1] - 250, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

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

cap.release()
cv2.destroyAllWindows()
