import cv2
import time
import numpy as np
from ultralytics import YOLO
import os

# ✅ Set Absolute Paths
MODEL_PATH = "D:/Lyra/lyra1.0/gen1/models/yolov8s.engine"  # Ensure correct model path
COCO_LABELS_PATH = "D:/Lyra/lyra1.0/gen1/models/coco.names"  # Ensure correct labels path

# ✅ Manually Set Camera Index (Change this if needed)
MANUAL_CAMERA_INDEX = 1  # Set to 0 for the default camera, 1 for external, etc.

# ✅ Load Class Names from COCO Dataset
def load_class_names(path):
    if not os.path.exists(path):
        print(f"❌ Error: {path} not found! Object names won't be displayed.")
        return []
    
    with open(path, "r") as f:
        return [line.strip() for line in f.readlines()]

# ✅ Try Manual Camera Index First, Then Auto-Detect
def find_working_camera():
    cap = cv2.VideoCapture(MANUAL_CAMERA_INDEX)  # Try manual selection first
    if cap.isOpened():
        print(f"✅ Using Manually Set Camera Index: {MANUAL_CAMERA_INDEX}")
    else:
        print(f"❌ Camera Index {MANUAL_CAMERA_INDEX} not found! Trying auto-detect...")
        for index in range(5):
            cap = cv2.VideoCapture(index)
            if cap.isOpened():
                print(f"✅ Using Auto-Detected Camera Index: {index}")
                break
        else:
            print("❌ No working camera found! Exiting...")
            exit()

    # ✅ Set Camera Resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)  # Set Width to Full HD
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)  # Set Height to Full HD
    cap.set(cv2.CAP_PROP_FPS, 30)  # Set FPS (if supported)

    # ✅ Confirm Resolution
    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    print(f"📷 Camera Resolution Set To: {int(width)}x{int(height)}")

    return cap

cap = find_working_camera()

# ✅ Load YOLO Model & Labels
print(f"🚀 Loading TensorRT Model from: {MODEL_PATH}")
model = YOLO(MODEL_PATH)
class_names = load_class_names(COCO_LABELS_PATH)

if not class_names:
    print("⚠️ No class names found! Object names won't be displayed.")

# ✅ Initialize FPS Calculation
prev_time = time.time()
fps_values = []

# ✅ Create Window Before Resizing (Fix OpenCV Error)
cv2.namedWindow("LYRA 1.0 Object Detection", cv2.WINDOW_NORMAL)
cv2.setWindowProperty("LYRA 1.0 Object Detection", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ Camera Not Detected!")
        break

    # ✅ Verify Frame Resolution
    print(f"📏 Frame Size: {frame.shape}")  # Debugging: Check actual resolution

    # ✅ Apply Night Vision Enhancement
    frame = cv2.convertScaleAbs(frame, alpha=1.5, beta=20)  # Adjust brightness & contrast

    # ✅ Run YOLO Inference
    results = model(frame)

    # ✅ Calculate FPS (Smoothed)
    curr_time = time.time()
    fps = 1 / (curr_time - prev_time)
    prev_time = curr_time

    fps_values.append(fps)
    if len(fps_values) > 10:  # Keep last 10 values for smoothing
        fps_values.pop(0)
    
    avg_fps = sum(fps_values) / len(fps_values)

    # ✅ Draw Detections
    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])  # Bounding box
            conf = float(box.conf[0])  # Confidence score
            cls = int(box.cls[0])  # Class ID

            # ✅ Get Class Name from COCO Dataset
            class_name = class_names[cls] if cls < len(class_names) else f"Class {cls}"

            # ✅ Draw Bounding Box & Label
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            label = f"{class_name} {conf:.2f}"
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    # ✅ Display FPS (Smoothed)
    cv2.putText(frame, f"FPS: {avg_fps:.2f}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)

    # ✅ Show Output Frame in Full Screen
    cv2.imshow("LYRA 1.0 Object Detection", frame)

    # ✅ Exit on 'Q' Key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# ✅ Release Resources
cap.release()
cv2.destroyAllWindows()
