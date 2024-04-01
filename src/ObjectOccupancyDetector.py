'''

            +----------------------------+
            | ObjectOccupancyDetector.py |
            +----------------------------+


This Python program contains all application "Park It!" system components:

    1. The Space Occupancy Monitor: A lightweight OpenCV algorithm for detecting
    differences in frame contours and pixel intensities. The intended use of this
    algorithm is to determine whether or not a defined parking space is occupied
    by some sort of object.

    2. The YOLOv5 Object Detector: A powerful Machine Learning algorithm for 
    the detection of real-world objects. In this case, the system only look 
    for cars. The intended use of this ML algorithm is to verify that the object
    occupying the parking space is indeed a vehicle.

    3. Pluto Connection Data Stream: A simple SSH session used for one-way
    data communication from the Park It! application server to the Pluto web 
    server. The intended use of this data stream is to relay system status 
    information so that the end-user can remotely check if the parking space
    is available.


'''

import cv2
import time
import numpy as np
from yolov5 import YOLOv5

# Custom libraries
from Adaptation import get_value_from_tag, update_xml_tag_value, log

# System Configuration File
sys_config = "src/ParkitConfiguration.xml"

# Read all configuration data by parsing XML file...
# Space Dimensions & Properties
rectx     = int(get_value_from_tag(sys_config, "space-x"))
recty     = int(get_value_from_tag(sys_config, "space-y"))
rectw     = int(get_value_from_tag(sys_config, "space-width"))
recth     = int(get_value_from_tag(sys_config, "space-height"))
move_dist = int(get_value_from_tag(sys_config, "move-dist"))
log(f"Space Dimensions: x={rectx}, y={recty}, width={rectw}, height={recth}, move-dist={move_dist}")

# YOLOv5 data
weights  = get_value_from_tag(sys_config, "weights")
resource = get_value_from_tag(sys_config, "resource")
log(f"YOLOv5: weights={weights}, device={resource}")

# Timers - used to track how long the space has been occupied
occupied_timer     = int(get_value_from_tag(sys_config, "occupied-timer"))
occupied_start_time = None

# Data - input and save locations
camera = int(get_value_from_tag(sys_config, "camera"))
prev_saved_rframe = get_value_from_tag(sys_config, "rframe-save-location")

# Variables and objects used in application...
# Rectangle parameters: [x, y, width, height]
# This is the rectangle box used for determining occupancy on a parking space
rect = [rectx, recty, rectw, recth]

# Load a pre-trained YOLOv5 model on the application server CPU
yolov5_model = YOLOv5(weights, device=resource)  

# Reference frame used when checking occupancy
# Use previously loaded reference frame if the status is marked as failed
if get_value_from_tag(sys_config, "status") == "failed":
    reference_frame = np.load(prev_saved_rframe)
    log(f"Previous reference frame found. Loading {prev_saved_rframe}")
else:
    reference_frame = None
    log("Using new reference frame.")

# Occupancy flag used for coloring the rectangle
confirmed_occupied = False

# System Status Messages
msg_occu = ""
msg_car = ""
last_car = ""
last_occu = ""

# check_occupation - Check if live video frame is occupied
def check_occupation(frame, rect, reference_frame):
    global occupied_start_time, confirmed_occupied

    # Obtain parking space rectangle location on frame
    x, y, w, h = rect

    # Reference of Interest: The video frame inside the space
    roi = frame[y:y+h, x:x+w]
    if reference_frame is not None:
        # Get the difference & convert to grey scale
        diff = cv2.absdiff(roi, reference_frame)
        gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        
        # Count the number of pixels above a certain insensity threshold
        _, thresh = cv2.threshold(gray, 25, 255, cv2.THRESH_BINARY)
        count = cv2.countNonZero(thresh)
        occupied = count > (w * h * 0.1) 

        # Start timer, this is used later in the main loop
        if occupied:
            if occupied_start_time is None:
                occupied_start_time = time.time()
        else:
            occupied_start_time = None
            confirmed_occupied = False

        return occupied, reference_frame

    return False, reference_frame

# Capture video from the webcam
cap = cv2.VideoCapture(camera)
if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read frame from webcam.")
        log("ERROR: Could not read frame from webcam.")
        break

    # Update the reference frame
    if reference_frame is None:
        x, y, w, h = rect
        reference_frame = frame[y:y+h, x:x+w].copy()
        # Save reference frame in case system crashes
        np.save(prev_saved_rframe, reference_frame)

    # Draw the rectangle and determine rectangle color
    rect_color = (0, 0, 255) if confirmed_occupied else (0, 255, 0)
    cv2.rectangle(frame, (rect[0], rect[1]), (rect[0]+rect[2], rect[1]+rect[3]), rect_color, 2)

    # Check if the space is occupied
    occupied, _ = check_occupation(frame, rect, reference_frame)
    if occupied and occupied_start_time:
        if time.time() - occupied_start_time > occupied_timer:
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
            if len(car_detections) > 0:
                msg_car = "CAR IN SPACE"          

                # Iterate through each car detection to draw a rectangle if the car is in the space
                for index, row in car_detections.iterrows():
                    class_name = row['name']
                    xmin, ymin, xmax, ymax = map(int, [row['xmin'], row['ymin'], row['xmax'], row['ymax']])
                    
                    if class_name == "car":
                        # Draw rectangle around the detected car
                        cv2.rectangle(frame, (xmin+rect[0], ymin+rect[1]), (xmax+rect[0], ymax+rect[1]), (255, 0, 0), 2)

            else:
                # Car is not in space
                msg_car = "CAR NOT IN SPACE"

            cv2.putText(frame, msg_car, (rect[0]+300, rect[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,0), 2)

    else:
        msg_occu = "SPACE NOT OCCUPIED"
        msg_car  = "CAR NOT IN SPACE"
        confirmed_occupied = False

    formated_data = f"{msg_occu} - {msg_car}"

    if msg_car != last_car:
        last_car = msg_car
        log(f"Status Update: New status='{formated_data}'")
        # Write after data here
        print(formated_data)
    
    if msg_occu != last_occu:
        last_occu = msg_occu
        log(f"Status Update: New status='{formated_data}'")
        # Write after data here
        print(formated_data)
    
    cv2.imshow('frame', frame)

    # Move the rectangle based on key presses
    # The box can move at any time while the application is running
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('w'):  # Move up
        rect[1] -= move_dist
        log("Space moved: UP")
    elif key == ord('s'):  # Move down
        rect[1] += move_dist
        log("Space moved: DOWN")
    elif key == ord('a'):  # Move left
        rect[0] -= move_dist
        log("Space moved: LEFT")
    elif key == ord('d'):  # Move right
        rect[0] += move_dist
        log("Space moved: RIGHT")
    elif key == ord('r'):  # Reset reference frame
        reference_frame = None
        confirmed_occupied = False
        log("Reference frame reset.")

    update_xml_tag_value(sys_config, "space-x", str(rect[0]))
    update_xml_tag_value(sys_config, "space-y", str(rect[1]))

cap.release()
cv2.destroyAllWindows()
