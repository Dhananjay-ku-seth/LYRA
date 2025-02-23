import cv2
import time
import numpy as np
from ultralytics import YOLO

# Load YOLO model with TensorRT
MODEL_PATH = "models/yolov8s.engine"  # Ensure correct path
COCO_LABELS_PATH = "models/coco.names"  # Ensure coco.names exists

# Load class names from COCO dataset
def load_class_names(path):
    try:
        with open(path, "r") as f:
            return [line.strip() for line in f.readlines()]
    except FileNotFoundError:
        print(f"❌ Error: {path} not found!")
        return []

# Set fixed camera index to 1 (External Camera)
camera_index = 1
cap = cv2.VideoCapture(camera_index)

if not cap.isOpened():
    print("❌ External camera not detected! Trying default camera...")
    cap = cv2.VideoCapture(0)

# Load model and labels
print(f"🚀 Loading TensorRT Model from: {MODEL_PATH}")
model = YOLO(MODEL_PATH)
class_names = load_class_names(COCO_LABELS_PATH)

if not class_names:
    print("❌ No class names found! Object names won't be displayed.")

# Start video capture
prev_time = 0

while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ Camera Not Detected!")
        break

    # Run YOLO inference
    results = model(frame)

    # Get FPS
    curr_time = time.time()
    fps = 1 / (curr_time - prev_time)
    prev_time = curr_time

    # Draw detections on frame
    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])  # Bounding box
            conf = float(box.conf[0])  # Confidence score
            cls = int(box.cls[0])  # Class ID

            # Get class name from COCO dataset
            class_name = class_names[cls] if cls < len(class_names) else f"Class {cls}"

            # Draw bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            # Display class name & confidence score
            label = f"{class_name} {conf:.2f}"
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    # Display FPS
    cv2.putText(frame, f"FPS: {fps:.2f}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)

    # Show frame
    cv2.imshow("LYRA 1.0 Object Detection", frame)

    # Exit on 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
