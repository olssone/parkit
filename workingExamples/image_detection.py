import torch
from PIL import Image

def load_image(image_path):
    # Load an image from the given path
    return Image.open(image_path)

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

if __name__ == "__main__":
    # Ask the user for an image file path
    image_path = input("Please enter the path to your image file: ")

    # Load the image
    image = load_image(image_path)

    # Detect objects in the image
    detected_objects = detect_objects(image)

    # Print detected objects
    print("Detected Objects:", detected_objects)

