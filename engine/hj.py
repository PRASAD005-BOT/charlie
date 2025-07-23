import os
import cv2
import pytesseract
import numpy as np
import time
from flask import Flask, request, jsonify

from werkzeug.utils import secure_filename

# Configure Flask app
app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Set Tesseract-OCR path (Modify if necessary)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Load YOLO model for object detection
net = cv2.dnn.readNet("C:/Users/vadla/Downloads/yolov3.weights", "C:/Users/vadla/Downloads/yolov3.cfg")

# Load class labels
with open("C:/Users/vadla/Downloads/coco.names", "r") as f:
    classes = [line.strip() for line in f.readlines()]

layer_names = net.getLayerNames()
out_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]


@app.route("/", methods=["GET"])
def home():
    """Home route to confirm the server is running."""
    return jsonify({"message": "Welcome to the Video OCR Detection API!"})


def preprocess_frame(frame):
    """Apply preprocessing techniques for OCR accuracy improvement."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                   cv2.THRESH_BINARY, 11, 2)
    return thresh


def extract_text(frame):
    """Extract text from a given frame using Tesseract OCR."""
    preprocessed = preprocess_frame(frame)
    text = pytesseract.image_to_string(preprocessed, config="--psm 6")
    return text.strip()


def compute_accuracy(extracted_text, ground_truth):
    """Compute OCR accuracy based on string similarity."""
    matches = sum(1 for a, b in zip(extracted_text, ground_truth) if a == b)
    return (matches / max(len(ground_truth), 1)) * 100 if ground_truth else 0


def detect_objects(frame):
    """Detect objects using YOLO and return the detected classes."""
    height, width, _ = frame.shape
    blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
    net.setInput(blob)
    detections = net.forward(out_layers)

    detected_objects = []
    for detection in detections:
        for obj in detection:
            scores = obj[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.5:
                detected_objects.append(classes[class_id])
    
    return list(set(detected_objects))


def process_video(video_path, ground_truth):
    """Process video, detect objects, extract text from frames, and compute accuracy."""
    cap = cv2.VideoCapture(video_path)
    frame_count = 0
    start_time = time.time()
    results = []
    total_accuracy = 0
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        text = extract_text(frame)
        objects = detect_objects(frame)
        accuracy = compute_accuracy(text, ground_truth)
        total_accuracy += accuracy
        
        results.append({"frame": frame_count, "text": text, "objects": objects, "accuracy": round(accuracy, 2)})

    cap.release()
    execution_time = time.time() - start_time
    avg_accuracy = total_accuracy / max(frame_count, 1)
    
    return {"OCR_Accuracy": round(avg_accuracy, 2), "Execution_Time": round(execution_time, 2), "Results": results}


@app.route("/upload", methods=["POST"])
def upload_video():
    """Handle video upload and processing."""
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)

    # Ground truth text (Modify based on expected text from signboards)
    ground_truth_text = request.form.get("ground_truth", "Sample Text")

    # Process video and get results
    result = process_video(file_path, ground_truth_text)
    
    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)
