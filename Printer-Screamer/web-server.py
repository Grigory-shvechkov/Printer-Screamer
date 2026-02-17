from flask import Flask, Response, jsonify
from flask_cors import CORS
from ultralytics import YOLO
import cv2
import time
import random
import os

app = Flask(__name__)
CORS(app)  # allow all origins

# -------------------------------
# YOLO model
# -------------------------------
model = YOLO("./best.pt")  # put your trained model here

# -------------------------------
# Webcam setup
# -------------------------------
cap = cv2.VideoCapture(0)  # change index if needed
target_size = (640, 640)
prev_time = time.time()
last_detections = {"fps": 0, "objects": []}


# -------------------------------
# Frame generator for MJPEG
# -------------------------------
def generate_frames():
    global prev_time, last_detections
    prev_time = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        # Resize for YOLO
        frame_resized = cv2.resize(frame, target_size)

        # Run YOLO on GPU
        results = model(frame_resized, device=0, verbose=False)

        # Annotate frame
        annotated_frame = results[0].plot()

        # Calculate FPS
        curr_time = time.time()
        fps = 1 / max(curr_time - prev_time, 1e-6)
        prev_time = curr_time

        # Process detections
        objects = []
        alert_triggered = False
        for det in results[0].boxes.data.tolist():  # [x1, y1, x2, y2, conf, class]
            obj = {
                "bbox": det[:4],
                "confidence": det[4],
                "class": int(det[5])
            }
            objects.append(obj)
            if det[4] >= 0.85:  # confidence threshold
                alert_triggered = True


        # Update last detections
        last_detections = {"fps": round(fps, 1), "objects": objects}

        # Encode frame as JPEG
        ret, buffer = cv2.imencode(".jpg", annotated_frame)
        frame_bytes = buffer.tobytes()

        # Yield as MJPEG
        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n")

# -------------------------------
# Flask routes
# -------------------------------
@app.route("/video")
def video_feed():
    return Response(generate_frames(),
                    mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route("/detections")
def get_detections():
    return jsonify(last_detections)

# -------------------------------
# Run server
# -------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False)
