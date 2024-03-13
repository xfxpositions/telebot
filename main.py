from utils import init_deepgram, init_live_transcription, start_audio_server, select_input_device

deepgram = init_deepgram()

device_index = select_input_device()

stream_url = start_audio_server(port=5001, device_index=device_index)

init_live_transcription(deepgram, stream_url=stream_url, language="tr")