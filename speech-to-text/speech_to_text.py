import sounddevice as sd
import torch
from transformers import WhisperProcessor, WhisperForConditionalGeneration

# Load Whisper model and processor
model_name = "openai/whisper-base"
processor = WhisperProcessor.from_pretrained(model_name)
model = WhisperForConditionalGeneration.from_pretrained(model_name)

# Ensure the model is forced to transcribe in Polish (language=pl)
model.config.forced_decoder_ids = processor.get_decoder_prompt_ids(language="pl")

# Function to transcribe audio chunks
def transcribe_audio_chunk(audio_chunk):
    # Preprocess audio for the Whisper model
    inputs = processor(audio_chunk, sampling_rate=16000, return_tensors="pt")
    with torch.no_grad():
        # Generate predictions
        predicted_ids = model.generate(inputs.input_features)
    # Decode the predictions
    transcription = processor.batch_decode(predicted_ids, skip_special_tokens=True)
    return transcription[0]

# Real-time transcription
def real_time_transcription(chunk_duration=1):
    print("Rozpoczęcie transkrypcji (naciśnij Ctrl+C, aby zakończyć)...")
    try:
        # Callback for real-time processing
        def callback(indata, frames, time, status):
            if status:
                print(f"Status: {status}")
            # Use the first channel for mono audio
            audio_chunk = indata[:, 0]
            transcription = transcribe_audio_chunk(audio_chunk)
            print(f"Transkrypcja: {transcription}")

        # Start audio stream
        with sd.InputStream(samplerate=16000, channels=1, dtype="float32", callback=callback, blocksize=int(chunk_duration * 16000)):
            print("Nagrywanie w czasie rzeczywistym...")
            while True:
                sd.sleep(200)  # Keep the stream alive (1 second per iteration)
    except KeyboardInterrupt:
        print("\nTranskrypcja zakończona.")

# Run the real-time transcription for 2-second chunks
real_time_transcription(chunk_duration=2)
