from utils.transcription import select_input_device, start_audio_server, list_audio_devices
import pyaudio

audio = pyaudio.PyAudio()
devices = list_audio_devices(audio)
print(devices)
device_index = 18
stream_url = start_audio_server(port=5003, device_index=device_index)
print("audio server url started")

while True:
        # Check if the Enter key has been pressed
        if input() == '':
            print("Program stopped.")
            break
