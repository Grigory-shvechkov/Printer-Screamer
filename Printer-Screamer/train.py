from ultralytics import YOLO
import os
import shutil

if __name__ == "__main__":
    model = YOLO("yolov8n.pt")

    results = model.train(
        data="data-set/data.yaml",
        epochs=50,
        imgsz=640,
        batch=16,  # adjust if GPU memory is low
        device=0,  # ensures GPU usage
        amp=True,  # mixed precision
        project="runs",
        name="train",
        exist_ok=True
    )

    # Copy best model to root of project
    weights_dir = os.path.join("runs", "detect", "train", "weights")
    best_model_path = os.path.join(weights_dir, "best.pt")
    shutil.copy(best_model_path, "./best.pt")
    print(f"Best model copied to ./best.pt")
