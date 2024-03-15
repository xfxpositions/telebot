from utils import init_deepgram, init_live_transcription, start_audio_server, select_input_device


device_index = select_input_device()

stream_url = start_audio_server(port=5001, device_index=device_index)
print("audio server url started")

while True:
        # Check if the Enter key has been pressed
        if input() == '':
            print("Program stopped.")
            break
