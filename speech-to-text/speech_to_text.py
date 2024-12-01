import sounddevice as sd
import torch
from transformers import WhisperProcessor, WhisperForConditionalGeneration
import paho.mqtt.client as mqtt
import numpy as np

# Konfiguracja MQTT
broker = "ydb8577e.ala.eu-central-1.emqxsl.com"
port = 8883
topic = "speech-to-text"
username = "test_user"
password = "1234"

# Funkcja do publikowania wiadomości przez MQTT
def publish_to_mqtt(text):
    client = mqtt.Client()
    client.username_pw_set(username, password)
    client.tls_set()  # Użyj domyślnych certyfikatów systemowych dla TLS
    try:
        client.connect(broker, port)
        result = client.publish(topic, text)
        client.disconnect()
        if result[0] == 0:
            print(f"Wysłano do MQTT: {text}")
        else:
            print(f"Błąd podczas wysyłania do MQTT: {text}")
    except Exception as e:
        print(f"Błąd MQTT: {e}")

# Konfiguracja modelu Whisper
model_name = "openai/whisper-base"
processor = WhisperProcessor.from_pretrained(model_name)
model = WhisperForConditionalGeneration.from_pretrained(model_name)
model.config.forced_decoder_ids = processor.get_decoder_prompt_ids(language="pl")

# Funkcja do transkrypcji audio
def transcribe_audio_chunk(audio_chunk):
    # Preprocesowanie audio dla modelu Whisper
    inputs = processor(audio_chunk, sampling_rate=16000, return_tensors="pt")
    with torch.no_grad():
        predicted_ids = model.generate(inputs.input_features)
    transcription = processor.batch_decode(predicted_ids, skip_special_tokens=True)
    return transcription[0]

# Funkcja do transkrypcji w czasie rzeczywistym
def real_time_transcription(chunk_duration):
    print("Rozpoczęcie transkrypcji (naciśnij Ctrl+C, aby zakończyć)...")
    audio_buffer = np.zeros((int(chunk_duration * 16000),), dtype="float32")
    try:
        # Callback do przetwarzania dźwięku
        def callback(indata, frames, time, status):
            nonlocal audio_buffer
            if status:
                print(f"Status: {status}")
            # Dodanie nowych danych do bufora
            audio_buffer = np.concatenate((audio_buffer, indata[:, 0]))[-int(chunk_duration * 16000):]
            if len(audio_buffer) >= int(chunk_duration * 16000):
                transcription = transcribe_audio_chunk(audio_buffer)
                print(f"Transkrypcja: {transcription}")
                publish_to_mqtt(transcription)

        # Rozpoczęcie strumienia audio
        with sd.InputStream(samplerate=16000, channels=1, dtype="float32", callback=callback, blocksize=int(chunk_duration * 16000)):
            print("Nagrywanie w czasie rzeczywistym...")
            while True:
                sd.sleep(1000)
    except KeyboardInterrupt:
        print("\nTranskrypcja zakończona.")

# Uruchomienie transkrypcji
real_time_transcription(5)
