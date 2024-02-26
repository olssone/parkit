import torch
from PIL import Image, ImageDraw

def load_image(image_path):
    # Load an image from the given path
    return Image.open(image_path)

def detect_objects(image):
    # Load the YOLOv5 model
    model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)

    # Perform inference
    results = model(image)

    # Extract bounding boxes and class indices
    bboxes = results.xyxy[0].tolist()  # Convert bounding boxes to a list
    detected_objects = [{'class_name': results.names[int(bbox[-1])], 'bbox': bbox} for bbox in bboxes]

    return detected_objects

def display_detected_objects(image, detected_objects):
    for obj in detected_objects:
        # Extract bounding box coordinates
        xmin, ymin, xmax, ymax = map(int, obj['bbox'][:4])

        # Crop the image around the bounding box
        crop = image.crop((xmin, ymin, xmax, ymax))

        # Display the cropped image with a nice message
        print(f"Detected: {obj['class_name']}")
        crop.show()

if __name__ == "__main__":
    # Ask the user for an image file path
    image_path = input("Please enter the path to your image file: ")

    # Load the image
    image = load_image(image_path)

    # Detect objects in the image
    detected_objects = detect_objects(image)

    # Display each detected object
    display_detected_objects(image, detected_objects)

