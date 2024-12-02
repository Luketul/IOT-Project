import paho.mqtt.client as mqtt
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

# Konfiguracja MQTT
MQTT_BROKER = "ydb8577e.ala.eu-central-1.emqxsl.com"  # Adres brokera MQTT
MQTT_PORT = 8883  # Port brokera MQTT
MQTT_TOPIC = "emqx/esp8266"  # Temat do subskrypcji

# Konfiguracja InfluxDB
INFLUXDB_URL = "http://influxdb:8086"  # Adres InfluxDB
INFLUXDB_TOKEN = "sRELd-y3LM3L-wJmBmdDDU1p4ggGYt3wWzFelTDVqTZUCThGqdjjMZwJRgbUGvmmAMiV_Bq1ssnjqixbbIib8Q=="  # Token dostępu do InfluxDB
INFLUXDB_ORG = "iot-temp"  # Organizacja InfluxDB
INFLUXDB_BUCKET = "temperatures"  # Bucket InfluxDB

# Połączenie z InfluxDB
client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
write_api = client.write_api(write_options=SYNCHRONOUS)


# Callback: Połączenie z brokerem
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Połączono z brokerem MQTT.")
        client.subscribe(MQTT_TOPIC)
    else:
        print(f"Nie udało się połączyć, kod błędu: {rc}")


# Callback: Otrzymanie wiadomości
def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode("utf-8")  # Dekodowanie wiadomości
        temperature = float(payload)  # Konwersja na float (zakładamy, że dane to liczby)
        print(f"Otrzymano dane: {temperature}°C z tematu {msg.topic}")

        # Tworzenie punktu w InfluxDB
        point = Point("temperature") \
            .tag("topic", msg.topic) \
            .field("value", temperature)

        # Zapis do InfluxDB
        write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=point)
        print("Dane zapisane w InfluxDB.")
    except Exception as e:
        print(f"Błąd: {e}")


# Konfiguracja klienta MQTT
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

# Łączenie z brokerem MQTT
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)

# Uruchomienie pętli MQTT
try:
    print("Subskrybent MQTT działa...")
    mqtt_client.loop_forever()
except KeyboardInterrupt:
    print("\nZatrzymano subskrybenta.")
finally:
    client.close()
