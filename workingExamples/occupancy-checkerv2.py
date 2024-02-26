import cv2
import numpy as np
import time

# Rectangle parameters: [x, y, width, height]
rect = [100, 100, 350, 225]  # Initial position and size (width > height)
reference_frame = None
occupied_start_time = None
confirmed_occupied = False
image_saved = False  # Flag to check if the image has been saved
move_dist = 5  # Distance to move the rectangle per key press
margin = 20  # Margin to expand the ROI

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

    # Draw the rectangle and the dot only if not confirmed occupied
    if not confirmed_occupied:
        cv2.rectangle(frame, (rect[0], rect[1]), (rect[0]+rect[2], rect[1]+rect[3]), (0, 255, 0), 2)
        center = (rect[0] + rect[2] // 2, rect[1] + rect[3] // 2)
        cv2.circle(frame, center, 10, (0, 255, 0), -1)

    # Check if the space is occupied
    occupied, _ = check_occupation(frame, rect, reference_frame)
    print(occupied)

    if occupied and occupied_start_time:
        if time.time() - occupied_start_time > 10:
            print("SPACE OCCUPIED")
            confirmed_occupied = True
            # Save the expanded frame without green lines and dot if not already saved
            if not image_saved:
                x, y, w, h = rect
                # Adjust the ROI considering the margin and frame boundaries
                x_expanded = max(x - margin, 0)
                y_expanded = max(y - margin, 0)
                w_expanded = min(w + 2 * margin, frame.shape[1] - x_expanded)
                h_expanded = min(h + 2 * margin, frame.shape[0] - y_expanded)
                expanded_roi = frame[y_expanded:y_expanded+h_expanded, x_expanded:x_expanded+w_expanded]
                cv2.imwrite('expanded_occupied_space.jpg', expanded_roi)
                image_saved = True
                print("Expanded image saved.")

    if not confirmed_occupied:
        cv2.imshow('frame', frame)

    # Move the rectangle based on key presses
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('w'):  # Move up
        rect[1] -= move_dist
    elif key == ord('s'):  # Move down
        rect[1] += move_dist
    elif key == ord('a'): 
        rect[0] -= move_dist
    elif key == ord('d'):  # Move right
        rect[0] += move_dist
    elif key == ord('r'):  # Reset reference frame and flags
        reference_frame = None
        confirmed_occupied = False
        image_saved = False  # Reset the saved image flag

cap.release()
cv2.destroyAllWindows()