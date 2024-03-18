from utils.transcription import init_deepgram, init_live_transcription, start_audio_server, select_input_device
from threading import Event
import time

# Initialize global variables to manage transcription state
toggle_transcription = None
transcription_running = False
first_run = True

def init_transcription():
    global toggle_transcription
    # Ensure transcription is only initialized once
    if toggle_transcription is None:
        # Initialize the Deepgram service
        deepgram = init_deepgram()
        # Select the input device for audio capture
        device_index = select_input_device()
        # Start the audio server and get the stream URL
        audio_stream_url = start_audio_server(port=5001, device_index=device_index)
        print(f"Stream URL: {audio_stream_url}")
        # Initialize live transcription with the obtained stream URL
        toggle_transcription = init_live_transcription(deepgram, stream_url=audio_stream_url, language="tr", textbox=None, toggle_event=toggle_transcription)

def start_transcription():
    global transcription_running, first_run
    
    if first_run:
        # Initialize transcription on the first run
        init_transcription()
        first_run = False
    
    # Toggle the transcription state between running and not running
    toggle_transcription()

    # Update the transcription running state
    transcription_running = not transcription_running
    # Print current state to the console
    print("Transcription started." if transcription_running else "Transcription stopped.")

if __name__ == "__main__":
    # Example usage: start transcription when the script runs
    start_transcription()

    # Keep the script running to capture transcription; adjust as needed
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping transcription and exiting...")
        # Ensure transcription is stopped before exiting if it's running
        if transcription_running:
            start_transcription()
