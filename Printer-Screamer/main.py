from ultralytics import YOLO
import cv2
import time

# Load your trained model
model = YOLO("best.pt")

# Open webcam (0 = default camera)
cap = cv2.VideoCapture(1,cv2.CAP_DSHOW)

# Set target frame size for faster inference
target_size = (640, 640)

# FPS calculation
prev_time = time.time()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Resize frame for faster processing
    frame_resized = cv2.resize(frame, target_size)

    # Run inference on GPU
    results = model(frame_resized, device=0)

    # Annotate frame
    annotated_frame = results[0].plot()

    # Calculate FPS
    curr_time = time.time()
    fps = 1 / (curr_time - prev_time)
    prev_time = curr_time

    # Display FPS on frame
    cv2.putText(annotated_frame, f"FPS: {fps:.1f}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Show annotated frame
    cv2.imshow("YOLO Detection", annotated_frame)

    # Exit on 'q' or ESC
    if cv2.waitKey(1) & 0xFF in [27, ord("q")]:
        break

cap.release()
cv2.destroyAllWindows()
