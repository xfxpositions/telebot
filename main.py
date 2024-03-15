from utils.transcription import init_deepgram, init_live_transcription, start_audio_server, select_input_device
from threading import Event  # Make sure you have this import


server_ready_event = Event()  # Create an event

deepgram = init_deepgram()
device_index = select_input_device()

# Pass the event to start_audio_server
stream_url = start_audio_server(port=5001, device_index=device_index, server_ready_event=server_ready_event)

# Wait for the server to be ready
server_ready_event.wait()

# Once the event is set, proceed to start live transcription
init_live_transcription(deepgram, stream_url=stream_url, language="tr")

