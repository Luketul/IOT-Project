import cv2
import torch
import paho.mqtt.client as mqtt
from ultralytics import YOLO
import json
import time

# Konfiguracja MQTT
MQTT_BROKER = "ydb8577e.ala.eu-central-1.emqxsl.com"
MQTT_PORT = 8883
MQTT_TOPIC = "yolov8/objects"
MQTT_USERNAME = "test_user"
MQTT_PASSWORD = "1234"

# Funkcja do publikowania wiadomości przez MQTT
def publish_to_mqtt(objects):
    client = mqtt.Client()
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    client.tls_set()  # Użyj domyślnych certyfikatów systemowych dla TLS
    try:
        client.connect(MQTT_BROKER, MQTT_PORT)
        payload = json.dumps({"objects": objects})
        result = client.publish(MQTT_TOPIC, payload)
        client.disconnect()
        if result[0] == 0:
            print(f"Wysłano do MQTT: {payload}")
        else:
            print(f"Błąd podczas wysyłania do MQTT: {payload}")
    except Exception as e:
        print(f"Błąd MQTT: {e}")

# Funkcja do detekcji obiektów
def detect_objects(frame, model):
    try:
        results = model(frame)  # Wykonanie detekcji
        result = results[0]  # Uzyskanie wyników z pierwszego obrazu
        labels = result.names  # Lista nazw klas
        boxes = result.boxes  # Detekcje (bounding boxes)

        if boxes and boxes.cls is not None:
            detected_objects = boxes.cls.cpu().numpy().astype(int)
            detected_classes = [labels[int(cls)] for cls in detected_objects]
            return detected_classes
        return []
    except Exception as e:
        print(f"Błąd detekcji: {e}")
        return []

# Funkcja główna do przetwarzania klatek
def process_video():
    print("Inicjalizacja YOLO...")
    model = YOLO("yolov8n.pt")  # Załaduj model YOLOv8

    print("Inicjalizacja kamery...")
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Błąd: Nie można otworzyć strumienia wideo.")
        return

    print("Rozpoczęcie przetwarzania (naciśnij 'q', aby zakończyć)...")
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Błąd: Nie można przechwycić klatki.")
                break

            # Wykrywanie obiektów
            detected_classes = detect_objects(frame, model)
            print(f"Znalezione obiekty: {detected_classes}")

            # Publikacja do MQTT
            if detected_classes:
                publish_to_mqtt(detected_classes)

            # Wyświetlanie ramki z detekcjami
            cv2.imshow("YOLOv8 - Obiekt Detection", frame)

            # Wyjście przy naciśnięciu 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        print("\nPrzerwano przetwarzanie.")
    except Exception as e:
        print(f"Błąd: {e}")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("Zakończono.")

# Uruchomienie detekcji
process_video()
