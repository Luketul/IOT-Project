#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <time.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// WiFi credentials
const char *ssid = "iPhone (Łukasz)";          // Replace with your WiFi name
const char *password = "kuszoton14";           // Replace with your WiFi password

// MQTT Broker settings
const int mqtt_port = 8883;                    // MQTT port (TLS)
const char *mqtt_broker = "ydb8577e.ala.eu-central-1.emqxsl.com";
const char *mqtt_topic_temp = "emqx/esp8266";  // MQTT topic for temperature
const char *mqtt_topic_objects = "yolov8/objects";
const char *mqtt_topic_speech = "speech-to-text";
const char *mqtt_username = "test_user";
const char *mqtt_password = "1234";

// NTP Server settings
const char *ntp_server = "pool.ntp.org";
const long gmt_offset_sec = 0;
const int daylight_offset_sec = 0;

// DS18B20 Sensor settings
#define ONE_WIRE_BUS D3
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);

// LCD display settings
LiquidCrystal_I2C lcd(0x3F, 16, 2);

// WiFi and MQTT client initialization
BearSSL::WiFiClientSecure espClient;
PubSubClient mqtt_client(espClient);

// SSL certificate for MQTT broker
static const char ca_cert[] PROGMEM = R"EOF(
-----BEGIN CERTIFICATE-----
MIIDrzCCApegAwIBAgIQCDvgVpBCRrGhdWrJWZHHSjANBgkqhkiG9w0BAQUFADBh
MQswCQYDVQQGEwJVUzEVMBMGA1UEChMMRGlnaUNlcnQgSW5jMRkwFwYDVQQLExB3
d3cuZGlnaWNlcnQuY29tMSAwHgYDVQQDExdEaWdpQ2VydCBHbG9iYWwgUm9vdCBD
QTAeFw0wNjExMTAwMDAwMDBaFw0zMTExMTAwMDAwMDBaMGExCzAJBgNVBAYTAlVT
MRUwEwYDVQQKEwxEaWdpQ2VydCBJbmMxGTAXBgNVBAsTEHd3dy5kaWdpY2VydC5j
b20xIDAeBgNVBAMTF0RpZ2lDZXJ0IEdsb2JhbCBSb290IENBMIIBIjANBgkqhkiG
9w0BAQEFAAOCAQ8AMIIBCgKCAQEA4jvhEXLeqKTTo1eqUKKPC3eQyaKl7hLOllsB
CSDMAZOnTjC3U/dDxGkAV53ijSLdhwZAAIEJzs4bg7/fzTtxRuLWZscFs3YnFo97
nh6Vfe63SKMI2tavegw5BmV/Sl0fvBf4q77uKNd0f3p4mVmFaG5cIzJLv07A6Fpt
43C/dxC//AH2hdmoRBBYMql1GNXRor5H4idq9Joz+EkIYIvUX7Q6hL+hqkpMfT7P
T19sdl6gSzeRntwi5m3OFBqOasv+zbMUZBfHWymeMr/y7vrTC0LUq7dBMtoM1O/4
gdW7jVg/tRvoSSiicNoxBN33shbyTApOB6jtSj1etX+jkMOvJwIDAQABo2MwYTAO
BgNVHQ8BAf8EBAMCAYYwDwYDVR0TAQH/BAUwAwEB/zAdBgNVHQ4EFgQUA95QNVbR
TLtm8KPiGxvDl7I90VUwHwYDVR0jBBgwFoAUA95QNVbRTLtm8KPiGxvDl7I90VUw
DQYJKoZIhvcNAQEFBQADggEBAMucN6pIExIK+t1EnE9SsPTfrgT1eXkIoyQY/Esr
hMAtudXH/vTBH1jLuG2cenTnmCmrEbXjcKChzUyImZOMkXDiqw8cvpOp/2PV5Adg
06O/nVsJ8dWO41P0jmP6P6fbtGbfYmbW0W5BjfIttep3Sp+dWOIrWcBAI+0tKIJF
PnlUkiaY4IBIqDfv8NZ5YBberOgOzW6sRBc4L0na4UU+Krk2U886UAb3LujEV0ls
YSEY1QSteDwsOoBrp+uvFRTp2InBuThs4pFsiv9kuXclVzDAGySj4dzp30d8tbQk
CAUw7C29C79Fv1C5qfPrmAESrciIxpg0X40KPMbp1ZWVbd4=
-----END CERTIFICATE-----
)EOF";

// Function declarations
void connectToWiFi();
void connectToMQTT();
void mqttCallback(char *topic, byte *payload, unsigned int length);
void publishTemperature();
void syncTime();

void setup() {
    lcd.init();
    lcd.backlight();
    Serial.begin(115200);

    connectToWiFi();
    syncTime(); // Synchronize time for SSL validation
    mqtt_client.setServer(mqtt_broker, mqtt_port);
    mqtt_client.setCallback(mqttCallback);
    connectToMQTT();
}

void connectToWiFi() {
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(1000);
        Serial.println("Connecting to WiFi...");
    }
    Serial.println("Connected to WiFi");
}

void syncTime() {
    configTime(gmt_offset_sec, daylight_offset_sec, ntp_server);
    while (time(nullptr) < 24 * 3600) { // Wait until time is synced
        delay(500);
        Serial.println("Waiting for NTP time sync...");
    }
    Serial.println("Time synchronized");
}

void connectToMQTT() {
    BearSSL::X509List serverTrustedCA(ca_cert);
    espClient.setTrustAnchors(&serverTrustedCA);
    while (!mqtt_client.connected()) {
        String client_id = "esp8266-client-" + String(WiFi.macAddress());
        Serial.printf("Connecting to MQTT Broker as %s...\n", client_id.c_str());
        if (mqtt_client.connect(client_id.c_str(), mqtt_username, mqtt_password)) {
            Serial.println("Connected to MQTT broker");
            mqtt_client.subscribe(mqtt_topic_objects);
            mqtt_client.subscribe(mqtt_topic_speech);
        } else {
            char err_buf[128];
            espClient.getLastSSLError(err_buf, sizeof(err_buf));
            Serial.print("Failed to connect to MQTT broker, rc=");
            Serial.println(mqtt_client.state());
            Serial.print("SSL error: ");
            Serial.println(err_buf);
            delay(5000);
        }
    }
}

void mqttCallback(char *topic, byte *payload, unsigned int length) {
    Serial.print("Message: ");
    Serial.print(topic);
    Serial.print("]: ");
    
    String message = "";
    for (int i = 0; i < length; i++) {
        message += (char) payload[i]; // Łączy wiadomość
    }
    Serial.println(message);

    // Jeśli temat to "speech-to-text", wyświetl na LCD
    if (String(topic) == "speech-to-text") {
        lcd.clear(); // Wyczyść wyświetlacz przed wyświetleniem nowej wiadomości
        lcd.setCursor(0, 0); // Ustaw kursor na początek pierwszej linii
        lcd.print(message);  // Wyświetl wiadomość na LCD
    }

    // Możesz dodać inne tematy, np. "yolov8/objects" i wyświetlić na LCD w podobny sposób
    if (String(topic) == "yolov8/objects") {
        lcd.clear(); // Wyczyść wyświetlacz przed wyświetleniem nowej wiadomości
        lcd.setCursor(0, 1); // Ustaw kursor na drugą linię
        lcd.print(message);  // Wyświetl wiadomość na LCD
    }
}


void publishTemperature() {
    sensors.requestTemperatures();
    float temperature = sensors.getTempCByIndex(0);
    if (temperature == DEVICE_DISCONNECTED_C) {
        Serial.println("Failed to read temperature from DS18B20!");
        return;
    }
    String tempStr = String(temperature);
    mqtt_client.publish(mqtt_topic_temp, tempStr.c_str());
    lcd.setCursor(0, 0);
    lcd.print("Temp: ");
    lcd.print(tempStr + " C   "); // Clear unused spaces
}

void loop() {
    if (!mqtt_client.connected()) {
        connectToMQTT();
    }
    mqtt_client.loop();

    // Publish temperature every 10 seconds
    static unsigned long lastTime = 0;
    unsigned long now = millis();
    if (now - lastTime > 10000) { // 10 seconds interval
        lastTime = now;
        publishTemperature();
    }
}
