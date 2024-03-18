# This Python script is the application system component for defining 
# a parking spot to monitor, detecting if the parking space is occupied, 
# and wether the object occupying the parking space is a "parkable" vehicle.

# We use the cv2 "OpenCV-Python" library for detecting space occupancy
# The YOLOv5 package is used for image detection
import cv2
from datetime import datetime
import paramiko
from yolov5 import YOLOv5

# System Logging Function
def log(message):
    logfile = "master_log"
    time = datetime.now()
    with open(logfile, "a") as file:
        file.write(f"{time} :: {message}\n")

# Clear the file and log starting message
logfile = "master_log"
time = datetime.now()
with open(logfile, "w") as file:
    file.write(f"{time} :: Starting Park It! system...\n")

# Rectangle parameters: [x, y, width, height]
# This is the rectangle box used for determining occupancy on a parking space
winput = int(input("Space Width: "))
hinput = int(input("Space Height: "))
rect = [500, 500, winput, hinput]

log(f"Space Dimensions [x,y,w,h]: {rect}")

# Load a pre-trained YOLOv5 model on the application server CPU
yolov5_model = YOLOv5("yolov5s.pt", device="cpu")  # You can choose from yolov5s, yolov5m, yolov5l, yolov5x

# This is how fast the user can move the box
move_dist = 50  # Distance to move the rectangle per key press

# Reference frame used when checking occupancy
reference_frame = None

# Car in Space Message
msg_car = ""

# last car msg
last_car = ""

# System Toggle
toggle = False

# Set up the SSH client and connect
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(hostname='pluto.hood.edu', username='eno1', password='hood10034685')

# Define data stream path and make sure it is clean
pluto_path = "~eno1/public_html/parkit/data.txt"
ssh.exec_command(f"rm -rf {pluto_path}")



# Capture video from the webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

# Main OpenCV video loop
while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read frame from webcam.")
        break

    # Draw the rectangle and determine rectangle color
    rect_color = (0, 0, 255)
    cv2.rectangle(frame, (rect[0], rect[1]), (rect[0]+rect[2], rect[1]+rect[3]), rect_color, 2)

    # Grab the Reference of Interest frame & run the pre-trained model on
    # the frame
    if toggle:
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


        cv2.putText(frame, msg_car, (rect[0], rect[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,0), 3)

    if msg_car != last_car:
        last_car = msg_car
        log(f"Status: {msg_car}")
        # Send data to Pluto
        stdin, stdout, stderr = ssh.exec_command(f"echo {msg_car} >> {pluto_path}")
    
    # Display OpenCV on frame
    cv2.imshow('frame', frame)

    # Move the rectangle based on key presses
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('w'):  # Move up
        rect[1] -= move_dist
        log(f"Move Up: Space at X:{rect[0]} Y:{rect[1]}")
    elif key == ord('s'):  # Move down
        rect[1] += move_dist
        log(f"Move Down: Space at X:{rect[0]} Y:{rect[1]}")
    elif key == ord('a'):  # Move left
        rect[0] -= move_dist
        log(f"Move Left: Space at X:{rect[0]} Y:{rect[1]}")
    elif key == ord('d'):  # Move right
        rect[0] += move_dist
        log(f"Move Right: Space at X:{rect[0]} Y:{rect[1]}")
    elif key == ord('i'):
        toggle = not toggle
        if toggle == True:
            log("Toggle: System ON")
        else:
            log("Toggle: System OFF")

# Clean Up Data file and OpenCV
stdin, stdout, stderr = ssh.exec_command(f"rm -rf {pluto_path}")
log("Park It! system terminated safely...")
cap.release()
cv2.destroyAllWindows()

