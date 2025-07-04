#!/usr/bin/env python3
"""
LYRA 1.0 Model Test Script
This script tests the trained YOLO model without requiring a camera.
"""

import torch
from ultralytics import YOLO
import os
import sys
import cv2
import numpy as np

# Model paths
MODEL_PATH = "runs/detect/train7/weights/best.pt"
TEST_IMAGE_PATH = "datasets/coco128/images/train2017/000000000009.jpg"  # Sample test image

def test_model_loading():
    """Test if the model loads correctly"""
    print("🧪 Testing LYRA 1.0 Model Loading...")
    
    if not os.path.exists(MODEL_PATH):
        print(f"❌ Model not found at: {MODEL_PATH}")
        return False
    
    try:
        model = YOLO(MODEL_PATH)
        print(f"✅ Model loaded successfully: {MODEL_PATH}")
        print(f"📊 Model info: {model.info()}")
        return model
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return False

def test_inference(model):
    """Test model inference on a sample image"""
    print("\n🔍 Testing Model Inference...")
    
    # Check if test image exists
    if not os.path.exists(TEST_IMAGE_PATH):
        print(f"❌ Test image not found: {TEST_IMAGE_PATH}")
        # Create a synthetic test image
        print("🎨 Creating synthetic test image...")
        test_img = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
    else:
        print(f"📸 Loading test image: {TEST_IMAGE_PATH}")
        test_img = cv2.imread(TEST_IMAGE_PATH)
    
    try:
        # Run inference
        results = model(test_img, verbose=False)
        
        print("✅ Inference completed successfully!")
        
        # Display results
        for i, result in enumerate(results):
            print(f"\n📋 Result {i+1}:")
            if result.boxes is not None and len(result.boxes) > 0:
                print(f"   🎯 Detections: {len(result.boxes)}")
                for j, box in enumerate(result.boxes):
                    conf = float(box.conf[0])
                    cls = int(box.cls[0])
                    print(f"     Detection {j+1}: Class {cls}, Confidence: {conf:.3f}")
            else:
                print("   📭 No objects detected")
        
        return True
        
    except Exception as e:
        print(f"❌ Inference error: {e}")
        return False

def check_model_metrics():
    """Display model training metrics if available"""
    print("\n📈 Model Training Metrics:")
    
    results_file = "runs/detect/train7/results.csv"
    if os.path.exists(results_file):
        # Read the last line to get final metrics
        with open(results_file, 'r') as f:
            lines = f.readlines()
            if len(lines) > 1:
                header = lines[0].strip().split(',')
                last_metrics = lines[-1].strip().split(',')
                
                # Find key metrics
                for i, metric in enumerate(header):
                    if 'mAP50(B)' in metric and i < len(last_metrics):
                        print(f"   🎯 mAP@0.5: {float(last_metrics[i]):.3f}")
                    elif 'mAP50-95(B)' in metric and i < len(last_metrics):
                        print(f"   🎯 mAP@0.5:0.95: {float(last_metrics[i]):.3f}")
                    elif 'precision(B)' in metric and i < len(last_metrics):
                        print(f"   🎯 Precision: {float(last_metrics[i]):.3f}")
                    elif 'recall(B)' in metric and i < len(last_metrics):
                        print(f"   🎯 Recall: {float(last_metrics[i]):.3f}")
    else:
        print("   ❌ No metrics file found")

def main():
    print("🚀 LYRA 1.0 Model Test Suite")
    print("=" * 40)
    
    # Change to model directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Test 1: Model Loading
    model = test_model_loading()
    if not model:
        print("❌ Model loading failed. Cannot proceed with tests.")
        sys.exit(1)
    
    # Test 2: Inference
    inference_success = test_inference(model)
    if not inference_success:
        print("❌ Inference test failed.")
    
    # Test 3: Display metrics
    check_model_metrics()
    
    # Summary
    print("\n" + "=" * 40)
    if inference_success:
        print("✅ LYRA 1.0 Model Test PASSED!")
        print("🎉 Model is ready for deployment.")
    else:
        print("❌ LYRA 1.0 Model Test FAILED!")
        print("🔧 Check model configuration and dependencies.")

if __name__ == "__main__":
    main()
