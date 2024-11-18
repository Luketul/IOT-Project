import cv2
import torch
import paho.mqtt.client as mqtt
from ultralytics import YOLO
import time

# Configurations for MQTT
MQTT_BROKER = "ydb8577e.ala.eu-central-1.emqxsl.com"  # Public MQTT broker (you can use your own broker)
MQTT_PORT = 8883
MQTT_TOPIC = "yolov8/objects"  # Topic to publish detected object names

# Initialize the YOLOv8 model (you can use different versions like yolov8n.pt, yolov8s.pt, etc.)
model = YOLO("yolov8n.pt")  # Load YOLOv8 Nano model

# Initialize MQTT Client
mqtt_client = mqtt.Client()
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)  # Connect to the broker

# Initialize webcam capture (0 is usually the default webcam)
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open video stream.")
    exit()

# Function to publish detected object names to MQTT
def publish_to_mqtt(object_names):
    for name in object_names:
        mqtt_client.publish(MQTT_TOPIC, name)  # Publish each detected object name to the MQTT topic
        print(f"Published: {name}")
        time.sleep(0.5)  # Delay between messages to prevent flooding

# Loop to read frames from the webcam and perform object detection
while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to capture frame.")
        break

    # Perform inference on the current frame
    results = model(frame)

    # Access the first result (since results is a list)
    result = results[0]

    # Get the object labels (class names) from the result
    labels = result.names  # List of labels (object class names)

    # Get the detected boxes (bounding boxes, classes, and confidence scores)
    boxes = result.boxes  # This contains the detection boxes

    # Extract the class indices, boxes (xywh), and confidence scores
    detected_objects = boxes.cls.cpu().numpy().astype(int)  # Class indices
    detected_boxes = boxes.xywh.cpu().numpy()  # Bounding box coordinates (xywh)
    detected_scores = boxes.conf.cpu().numpy()  # Confidence scores

    # Convert the class indices to class names
    detected_classes = [labels[int(cls)] for cls in detected_objects]

    # Display the detected objects as words in the terminal
    detected_objects_str = "Detected Objects: " + ", ".join(detected_classes)
    print(detected_objects_str)

    # Publish detected object names to MQTT
    publish_to_mqtt(detected_classes)

    # Optional: Display the frame with bounding boxes and labels (for visualization)
    for bbox, cls in zip(detected_boxes, detected_objects):
        x, y, w, h = bbox
        label = labels[int(cls)]
        cv2.rectangle(frame, (int(x - w / 2), int(y - h / 2)), (int(x + w / 2), int(y + h / 2)), (0, 255, 0), 2)
        cv2.putText(frame, label, (int(x - w / 2), int(y - h / 2) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

    # Display the frame (for visualization)
    cv2.imshow("YOLOv8 Object Detection", frame)

    # Exit if the 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the capture and close the OpenCV window
cap.release()
cv2.destroyAllWindows()
