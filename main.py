from utils import init_deepgram, init_live_transcription, start_audio_server

deepgram = init_deepgram()

stream_url = start_audio_server(port=5001)

init_live_transcription(deepgram, stream_url=stream_url, language="tr-TR")