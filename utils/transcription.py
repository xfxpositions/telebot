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
import tkinter as tk
from threading import Event

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
        sentence = result.channel.alternatives[0].transcript
        if len(sentence) == 0:
            return
        print(f"transcription: {sentence}")

    def on_metadata(self, metadata, **kwargs):
        return
        
    def on_error(self, error, **kwargs):
        print(f"\n\n{error}\n\n")
        
    # STEP 4: Register the event handlers
    dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)
    dg_connection.on(LiveTranscriptionEvents.Metadata, on_metadata)
    dg_connection.on(LiveTranscriptionEvents.Error, on_error)
    
    config = LiveOptions(model="nova-2", language=language, channels=1, smart_format=True)
    
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

def sound_stream(device_index: int):
    # start Recording
        
    audio = pyaudio.PyAudio()
    
    
    # Define audio config
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    CHUNK = 1024
    BITS_PER_SAMPLE = 16
    DEVICE_INDEX = device_index
    
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




def init_stream_audio(port, device_index:int):

    app = Flask(__name__)

    @app.route("/audio")
    def audio():
        return Response(sound_stream(device_index))

    @app.route('/')
    def index():
        """Video streaming home page."""
        return render_template('index.html')
    print(f"Audio streaming started at http://localhost:{port}/audio")
    app.run(debug=False, threaded=True, port=port)
    
def start_audio_server(port, device_index: int, server_ready_event: Event):
    def run_server():
        app = Flask(__name__)

        @app.route("/audio")
        def audio():
            return Response(sound_stream(device_index))

        @app.route('/')
        def index():
            """Video streaming home page."""
            return render_template('index.html')

        @app.before
        def activate_server_ready():
            server_ready_event.set()

        print(f"Audio streaming started at http://localhost:{port}/audio")
        app.run(debug=False, threaded=True, port=port)

    stream_thread = threading.Thread(target=run_server)
    stream_thread.daemon = True
    stream_thread.start()

def get_api_info(p: pyaudio.PyAudio):
    PREFERRED_HOST_API_NAME = 'Windows WASAPI'
    api_info, api_index = None, 0
    for i in range(p.get_host_api_count()):
        current_api_info = p.get_host_api_info_by_index(i)
        if i == 0:
            api_info = current_api_info
        else:
            if current_api_info['name'] == PREFERRED_HOST_API_NAME:
                api_info, api_index = current_api_info, i
                break
    return api_info, api_index

def list_audio_devices(p: pyaudio.PyAudio):
    PREFERRED_HOST_API_NAME = 'Windows WASAPI'
    devices = []
    api_info, api_index = get_api_info(p)
    api_name = api_info['name']
    if api_name != PREFERRED_HOST_API_NAME:
        print(f'[WARNING] "{PREFERRED_HOST_API_NAME}" not available on this system, '
            f'going with "{api_name}" instead')
 
    numdevices = api_info.get('deviceCount')
    for i in range(numdevices):
        dev_info = p.get_device_info_by_host_api_device_index(api_index, i)
        if dev_info.get('maxInputChannels') > 0:
            devices.append(dev_info.get("name"))
    return devices

def select_input_device():
    p = pyaudio.PyAudio()
    device_list = list_audio_devices(p)
    for i, device in enumerate(device_list):
        print(f"{i + 1}. {device}")
 
    selected_device_index = None
    while True:
        try:
            selected_device_index = int(input("Please select an input device by entering its index: "))
            if selected_device_index < 1 or selected_device_index > len(device_list):
                raise ValueError("Invalid index. Please enter a valid index.")
            break
        except ValueError as ve:
            print(ve)
 
    return selected_device_index - 1  # Adjusting index to match Python's zero-based indexing