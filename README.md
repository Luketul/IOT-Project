# Speech-to-Text and Video-to-Text Application with Temperature Measurement and Visualization in Grafana

## Project Description

This project involves creating an application with the following functionalities:
1. **Temperature Measurement** – The ESP8266 microcontroller measures temperature using the DS18B20 sensor. The read data is sent to a remote MQTT broker.
2. **Speech-to-Text Conversion** – A program using the Whisper model converts Polish speech to text and sends the result to the MQTT broker.
3. **Video-to-Text Conversion** – A program using the YOLO model detects objects in a video and names them as text, sending the result to the MQTT broker.
4. **Displaying Results on an LCD** – The ESP8266 receives text (from speech or video) and displays it on an LCD screen.
5. **Data Collection and Visualization** – Temperature data is saved to an InfluxDB database and visualized using Grafana.

All components are connected via an MQTT broker. The application is run in virtual environments (venv) and Docker containers. The entire project is organized in a Git repository that contains source code and documentation.

## Technologies

- **ESP8266** – Microcontroller with DS18B20 sensor for temperature measurement
- **MQTT** – Communication protocol for sending data between applications
- **InfluxDB** – Database for storing temperature data
- **Grafana** – Tool for visualizing data from InfluxDB
- **Whisper** – Model for speech recognition and transcription
- **YOLO** – Model for object detection in video
- **Docker** – Containerization platform for running applications (InfluxDB, Grafana, subscriber)
- **Python** – Programming language used for "subscriber", "speech-to-text", and "video-to-text" applications


