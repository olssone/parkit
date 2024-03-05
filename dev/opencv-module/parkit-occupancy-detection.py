# This Python script is the application system component for defining 
# a parking spot to monitor, detecting if the parking space is occupied, 
# and wether the object occupying the parking space is a "parkable" vehicle.

# We use the cv2 "OpenCV-Python" library for detecting space occupancy
import cv2
import numpy as np
import time

# The YOLOv5 package is used for image detection
from yolov5 import YOLOv5

# Load a pre-trained YOLOv5 model on the application server CPU
yolov5_model = YOLOv5("yolov5s.pt", device="cpu")  # You can choose from yolov5s, yolov5m, yolov5l, yolov5x

# Rectangle parameters: [x, y, width, height]
# This is the rectangle box used for determining occupancy on a parking space
rect = [200, 200, 500, 225]

# This is how fast the user can move the box
move_dist = 5  # Distance to move the rectangle per key press

# Reference frame used when checking occupancy
reference_frame = None

# Timer used to detect if the frame has been occupiued for longer than 10 seconds
occupied_start_time = None

# Occupancy flag used for coloring the rectangle
confirmed_occupied = False

# Occupancy Message
msg_occu = ""

# Car in Space Message
msg_car = ""

# check_occupation - Check if live video frame is occupied
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

    # Draw the rectangle and determine rectangle color
    rect_color = (0, 0, 255) if confirmed_occupied else (0, 255, 0)
    cv2.rectangle(frame, (rect[0], rect[1]), (rect[0]+rect[2], rect[1]+rect[3]), rect_color, 2)
    


    # Check if the space is occupied
    occupied, _ = check_occupation(frame, rect, reference_frame)

    if occupied and occupied_start_time:
        if time.time() - occupied_start_time > 10:
            msg_occu = "SPACE OCCUPIED"
            cv2.putText(frame, msg_occu, (rect[0], rect[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
            confirmed_occupied = True
            
            # Grab the Reference of Interest frame & run the pre-trained model on
            # the frame
            roi = frame[rect[1]:rect[1]+rect[3], rect[0]:rect[0]+rect[2]]
            results = yolov5_model.predict(roi)
            
            # Convert the results to a Pandas DataFrame for post-processing
            predictions_df = results.pandas().xyxy[0]  

            # Filter predictions for 'car' detections
            car_detections = predictions_df[predictions_df['name'] == 'car']

            if len(car_detections) <= 0:
                msg_car = "CAR NOT IN SPACE"
            else:
                # Iterate through each car detections to determine if car is in the rectange
                for index, row in car_detections.iterrows():
                    # Extract class name
                    class_name = row['name'] 
                    # Define system status message for car in space
                    if class_name == "car":
                        msg_car = "CAR IN SPACE"
        
                # Draw rectangles around detected objects only in the parking space rectangle
                # xyxy is for [xmin, ymin, xmax, ymax, confidence, class]
                for result in results.xyxy[0]: 
                    xmin, ymin, xmax, ymax= map(int, result[:4])
                    cv2.rectangle(frame, (xmin+rect[0], ymin+rect[1]), (xmax+rect[0], ymax+rect[1]), (255, 0, 0), 2)

            cv2.putText(frame, msg_car, (rect[0]+50, rect[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,0), 2)
    else:
        msg_occu = "SPACE NOT OCCUPIED"
        confirmed_occupied = False

    print(f"{msg_occu} - {msg_car}")


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