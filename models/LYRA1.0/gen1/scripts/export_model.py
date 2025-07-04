import os
from ultralytics import YOLO

# ✅ Ensure models/ folder exists
os.makedirs("models", exist_ok=True)

# ✅ Load YOLOv8-S Model
model = YOLO("yolov8s.pt")

# ✅ Export TensorRT Model
print("🚀 Exporting YOLOv8 to TensorRT...")
model.export(format="engine", device="cuda")

# ✅ Move Exported Model to models/ Folder
if os.path.exists("yolov8s.engine"):
    os.rename("yolov8s.engine", "models/yolov8s.engine")

print("✅ TensorRT Model Exported Successfully to models/yolov8s.engine! 🚀")
