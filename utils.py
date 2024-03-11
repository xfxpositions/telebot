from deepgram import (
    DeepgramClient,
    LiveTranscriptionEvents,
    LiveOptions,
)
import httpx
import threading
import os
from dotenv import load_dotenv
import pyaudio
from flask import Flask, Response,render_template



def init_deepgram():
    
    load_dotenv()
    
    API_KEY = os.getenv("DG_API_KEY")

    deepgram = DeepgramClient(API_KEY)
    
    return deepgram

def init_live_transcription(deepgram: DeepgramClient, stream_url: str, language: str):

    # STEP 2: Create a websocket connection to Deepgram
    dg_connection = deepgram.listen.live.v("1")

    # STEP 3: Define the event handlers for the connection
    def on_message(self, result, **kwargs):
        # print(f"result: {result}")
        sentence = result.channel.alternatives[0].transcript
        if len(sentence) == 0:
            return
        print(f"transcription: {sentence}")
        
    def on_metadata(self, metadata, **kwargs):
        print(f"\n\n{metadata}\n\n")
        
    def on_error(self, error, **kwargs):
        print(f"\n\n{error}\n\n")
        
    # STEP 4: Register the event handlers
    dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)
    dg_connection.on(LiveTranscriptionEvents.Metadata, on_metadata)
    dg_connection.on(LiveTranscriptionEvents.Error, on_error)
    
    config = LiveOptions(model="nova-2", language=language, channels=1, smart_format=False)
    
    # STEP 6: Start the connection
    
    dg_connection.start(config)
    
    # STEP 7: Create a lock and a flag for thread synchronization
    lock_exit = threading.Lock()
    exit = False
    
    # STEP 8: Define a thread that streams the audio and sends it to Deepgram
    def myThread():
        with httpx.stream("GET", stream_url) as r:
            for data in r.iter_bytes():
                lock_exit.acquire()
                if exit:
                    break
                lock_exit.release()

                dg_connection.send(data)
            # STEP 9: Start the thread
            
    myHttp = threading.Thread(target=myThread)
    myHttp.start()
    # STEP 10: Wait for user input to stop recording
    input("Press Enter to stop recording...\n\n")

    # STEP 11: Set the exit flag to True to stop the thread
    lock_exit.acquire()
    exit = True
    lock_exit.release()

    # STEP 12: Wait for the thread to finish
    myHttp.join()

    # STEP 13: Close the connection to Deepgram
    dg_connection.finish()

    print("Finished")
    
    
def gen_wav_header(sampleRate, bitsPerSample, channels):
    datasize = 2000*10**6
    o = bytes("RIFF",'ascii')                                               # (4byte) Marks file as RIFF
    o += (datasize + 36).to_bytes(4,'little')                               # (4byte) File size in bytes excluding this and RIFF marker
    o += bytes("WAVE",'ascii')                                              # (4byte) File type
    o += bytes("fmt ",'ascii')                                              # (4byte) Format Chunk Marker
    o += (16).to_bytes(4,'little')                                          # (4byte) Length of above format data
    o += (1).to_bytes(2,'little')                                           # (2byte) Format type (1 - PCM)
    o += (channels).to_bytes(2,'little')                                    # (2byte)
    o += (sampleRate).to_bytes(4,'little')                                  # (4byte)
    o += (sampleRate * channels * bitsPerSample // 8).to_bytes(4,'little')  # (4byte)
    o += (channels * bitsPerSample // 8).to_bytes(2,'little')               # (2byte)
    o += (bitsPerSample).to_bytes(2,'little')                               # (2byte)
    o += bytes("data",'ascii')                                              # (4byte) Data Chunk Marker
    o += (datasize).to_bytes(4,'little')                                    # (4byte) Data size in bytes
    return o

def sound_stream():
    # start Recording
        
    audio = pyaudio.PyAudio()
    
    
        # Define audio config
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    CHUNK = 1024
    RECORD_SECONDS = 5
    BITS_PER_SAMPLE = 16
    DEVICE_INDEX = 1
    
    # Generate header
    wav_header = gen_wav_header(RATE, BITS_PER_SAMPLE, CHANNELS)

    # Define stream
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, input=True,input_device_index=DEVICE_INDEX,
                    frames_per_buffer=CHUNK)
    
    print("recording...")
    
    first_run = True
    while True:
        # Add wav header if this is the first run
        if first_run:
            data = wav_header + stream.read(CHUNK)
            first_run = False
        else:
            data = stream.read(CHUNK)
        yield(data)



def init_stream_audio(port):

    app = Flask(__name__)

    @app.route("/audio")
    def audio():
        return Response(sound_stream())

    @app.route('/')
    def index():
        """Video streaming home page."""
        return render_template('index.html')
    print(f"Audio streaming started at http://localhost:{port}/audio")
    app.run(debug=False, threaded=True,port=port)
    
def start_audio_server(port):
    stream_thread = threading.Thread(target=init_stream_audio, args=(port,))

    stream_thread.daemon = True
    stream_thread.start()
    
    stream_url = f"http://localhost:{port}/audio"
    
    print(f"Audio stream server started on port {port}")
    
    return stream_url
    