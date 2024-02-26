import cv2
import time
import torch

# Load YOLOv5 model
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)

# Initialize camera
cap = cv2.VideoCapture(0)

# Initial position of the green box
x, y, w, h = 100, 100, 200, 200

# How fast box will move
movement = 20

# Flags and timers
occupied_since = None
occupied = False

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Draw the green box
    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # Check if space is occupied (simple example, adjust as needed)
    # This can be replaced with a more sophisticated occupancy check
    roi = frame[y:y+h, x:x+w]
    variance = cv2.Laplacian(roi, cv2.CV_64F).var()
    if variance > 50:  # Threshold for occupancy, adjust as needed
        if not occupied:
            occupied_since = time.time()
            occupied = True
    else:
        occupied_since = None
        occupied = False

    # If occupied for more than 10 seconds, detect objects
    if occupied and (time.time() - occupied_since) > 10:
        # Convert frame to the format YOLOv5 expects
        results = model(roi)
        if "car" in results:
            car_detected = True
            occupied_since = None  # Reset timer
            occupied = False
        else:
            car_detected = False
        

    cv2.imshow('Camera Feed', frame)

    if occupied:
        if car_detected:
            cv2.putText(frame, "Car is parked", (frame.shape[1] - 200, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        else:
            cv2.putText(frame, "Car is not parked", (frame.shape[1] - 250, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

    # Move the green box with arrow keys
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):  # Quit
        break
    elif key == 82:  # Up
        y = max(0, y - movement)
    elif key == 84:  # Down
        y = min(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) - h, y + movement)
    elif key == 81:  # Left
        x = max(0, x - movement)
    elif key == 83:  # Right
        x = min(cap.get(cv2.CAP_PROP_FRAME_WIDTH) - w, x + movement)

# Release resources
cap.release()
cv2.destroyAllWindows()
