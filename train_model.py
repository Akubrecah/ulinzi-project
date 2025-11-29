import os
from ultralytics import YOLO

def print_deprecation_notice():
    print("="*80)
    print("⚠️  DEPRECATION NOTICE:")
    print("This script is for training a local YOLOv8 model. The project's `detector.py` has been updated to use the Roboflow Hosted API instead. Therefore, running this training script will not affect the main detection logic.")
    print("="*80)

def train_yolo():
    # Load the nano model (fastest for CPU/Laptop)
    model = YOLO('yolov8n.yaml').load('yolov8n.pt')

    print("🚀 Starting training")
    
    # Get the absolute path to the data.yaml file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_yaml_path = os.path.join(script_dir, 'data.yaml')

    # Train the model
    # Ensure 'data.yaml' exists in the folder from the Roboflow download
    results = model.train(
    data=data_yaml_path,
    batch=16,
    epochs=50,
    imgsz=640,
    device="cpu"
    )
    
    print("✅ Training complete.")
    print("⚠️  ACTION REQUIRED: Copy 'runs/detect/train/weights/best.pt' to your main folder and rename it to 'yolo_model.pt'")

if __name__ == "__main__":
    # print_deprecation_notice() # Commented out as the deprecation notice is no longer needed.
    train_yolo()
