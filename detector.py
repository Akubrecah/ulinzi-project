from ultralytics import YOLO
import cv2
import os
import numpy as np
from PIL import Image

# Check if model exists to prevent crashes
model_path = "yolo_model.pt"
if os.path.exists(model_path):
    model = YOLO(model_path)
else:
    print(f"⚠️ Warning: {model_path} not found. Training needed.")
    model = None

def detect_objects(image: Image.Image):
    if model is None:
        return np.array(image)

    # Convert PIL image to OpenCV format
    img_np = np.array(image)
    
    # Run inference
    results = model.predict(img_np)
    result = results[0]
    
    # Draw boxes
    image_with_boxes = result.plot()
    
    return image_with_boxes

def find_anomalies_yolo(new_image_path):
    if model is None:
        return [], new_image_path

    # Run inference
    results = model.predict(new_image_path)
    result = results[0]
    
    # Draw boxes
    image_with_boxes = result.plot()
    
    # Save output (Linux path handling)
    annotated_path = "annotated_scan.png"
    cv2.imwrite(annotated_path, image_with_boxes)
    
    detected_anomalies = []
    
    # Extract data
    boxes = result.boxes.cpu().numpy()
    for box in boxes:
        # Assuming class 0 is the target
        if int(box.cls[0]) == 0:
            x1, y1, x2, y2 = box.xyxy[0].astype(int)
            cX = int((x1 + x2) / 2)
            cY = int((y1 + y2) / 2)
            confidence = float(box.conf[0])
            detected_anomalies.append((cX, cY, confidence))
            
    return detected_anomalies, annotated_path