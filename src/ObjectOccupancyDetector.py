# This Python script is the application system component for defining 
# a parking spot to monitor, detecting if the parking space is occupied, 
# and wether the object occupying the parking space is a "parkable" vehicle.

# We use the cv2 "OpenCV-Python" library for detecting space occupancy
import cv2
import time
import paramiko

# The YOLOv5 package is used for image detection
from yolov5 import YOLOv5

# Load a pre-trained YOLOv5 model on the application server CPU
yolov5_model = YOLOv5("yolov5/yolov5s.pt", device="cpu")  # You can choose from yolov5s, yolov5m, yolov5l, yolov5x

# Rectangle parameters: [x, y, width, height]
# This is the rectangle box used for determining occupancy on a parking space
rect = [500, 500, 500, 225]

# This is how fast the user can move the box
move_dist = 50  # Distance to move the rectangle per key press

# Reference frame used when checking occupancy
reference_frame = None

# Timer used to detect if the frame has been occupiued for over a period of time
occupied_start_time = None
occupied_timer = 10

# Timer used to determine if a car has been in a space for over a period of time
car_in_space_time = None
car_in_space_timer = 5

# Occupancy flag used for coloring the rectangle
confirmed_occupied = False

# Occupancy Message
msg_occu = ""

# Car in Space Message
msg_car = ""

# last car msg
last_car = ""

#last occu msg
last_occu = ""

# Set up the SSH client
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
# Connect to the server
ssh.connect(hostname='pluto.hood.edu', username='eno1', password='hood10034685')

# Define data stream path and make sure it is clean
pluto_path = "~eno1/public_html/parkit/data.txt"
ssh.exec_command(f"rm -rf {pluto_path}")

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

                # Check to see if timer has not been started yet
                if car_in_space_time is None:
                    car_in_space_time = time.time()
                

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
                # Reset timer
                car_in_space_time = None

            cv2.putText(frame, msg_car, (rect[0]+300, rect[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,0), 2)

    else:
        msg_occu = "SPACE NOT OCCUPIED"
        msg_car = "CAR NOT IN SPACE"
        confirmed_occupied = False
    
    formated_data = f"{msg_occu} - {msg_car}"

    if msg_car != last_car:
        last_car = msg_car
        stdin, stdout, stderr = ssh.exec_command(f"echo {formated_data}")
    
    if msg_occu != last_occu:
        last_occu = msg_occu
        stdin, stdout, stderr = ssh.exec_command(f"echo {formated_data}")


    


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

    # Error logging and such...

cap.release()
cv2.destroyAllWindows()
