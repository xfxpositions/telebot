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
from flask import Flask, Response, render_template
import tkinter as tk
from threading import Event
import sounddevice as sd


# Loads environment variables and initializes DeepgramClient with API key.
def init_deepgram():

    load_dotenv()

    API_KEY = os.getenv("DG_API_KEY")

    deepgram = DeepgramClient(API_KEY)

    return deepgram


# Sets up live transcription from an audio stream URL using DeepgramClient.
def init_live_transcription(
    deepgram: DeepgramClient,
    stream_url: str,
    language: str,
    textbox,
    toggle_event: threading.Event,
):
    print("LIVE TRANSCRIPTION FUNCTION WORKING")
    stream_url = "http://localhost:5003/audio"

    # STEP 2: Define a function to handle streaming and transcription
    def handle_stream():
        dg_connection = deepgram.listen.live.v("1")

        def on_message(self, result, **kwargs):
            sentence = result.channel.alternatives[0].transcript
            if len(sentence) == 0:
                return
            print(f"transcription: {sentence}")

            if textbox is not None:
                textbox.insert(tk.END, f"\n{sentence}")

        def on_metadata(self, metadata, **kwargs):
            return

        def on_error(self, error, **kwargs):
            print(f"\n\n{error}\n\n")

        dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)
        dg_connection.on(LiveTranscriptionEvents.Metadata, on_metadata)
        dg_connection.on(LiveTranscriptionEvents.Error, on_error)

        config = LiveOptions(
            model="nova-2", language=language, channels=1, smart_format=True
        )
        dg_connection.start(config)

        def stream_audio():
            with httpx.stream("GET", stream_url) as r:
                for data in r.iter_bytes():
                    if toggle_event.is_set():
                        break
                    dg_connection.send(data)

            dg_connection.finish()
            print("Finished Streaming")

        audio_thread = threading.Thread(target=stream_audio)
        audio_thread.start()
        return audio_thread

    # Initialize control variables
    audio_thread = None
    toggle_event = threading.Event()

    # STEP 3: Define a toggle function to start or stop transcription
    def toggle_transcription():
        nonlocal audio_thread
        if audio_thread is None or not audio_thread.is_alive():
            # Clear the event to start transcription
            toggle_event.clear()
            audio_thread = handle_stream()
            print("Transcription started.")
        else:
            # Set the event to stop transcription
            toggle_event.set()
            audio_thread.join()
            audio_thread = None
            print("Transcription stopped.")

    return toggle_transcription


# Generates a WAV file header for raw audio data.
def gen_wav_header(sampleRate, bitsPerSample, channels):
    datasize = 2000 * 10**6
    o = bytes("RIFF", "ascii")  # (4byte) Marks file as RIFF
    o += (datasize + 36).to_bytes(
        4, "little"
    )  # (4byte) File size in bytes excluding this and RIFF marker
    o += bytes("WAVE", "ascii")  # (4byte) File type
    o += bytes("fmt ", "ascii")  # (4byte) Format Chunk Marker
    o += (16).to_bytes(4, "little")  # (4byte) Length of above format data
    o += (1).to_bytes(2, "little")  # (2byte) Format type (1 - PCM)
    o += (channels).to_bytes(2, "little")  # (2byte)
    o += (sampleRate).to_bytes(4, "little")  # (4byte)
    o += (sampleRate * channels * bitsPerSample // 8).to_bytes(4, "little")  # (4byte)
    o += (channels * bitsPerSample // 8).to_bytes(2, "little")  # (2byte)
    o += (bitsPerSample).to_bytes(2, "little")  # (2byte)
    o += bytes("data", "ascii")  # (4byte) Data Chunk Marker
    o += (datasize).to_bytes(4, "little")  # (4byte) Data size in bytes
    return o


# Creates a generator that captures live audio from a specified device and yields data chunks.
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
    stream = audio.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        input_device_index=DEVICE_INDEX,
        frames_per_buffer=CHUNK,
    )

    print("recording...")

    first_run = True
    while True:
        # Add wav header if this is the first run
        if first_run:
            data = wav_header + stream.read(CHUNK)
            first_run = False
        else:
            data = stream.read(CHUNK)
        yield (data)


# Starts a separate thread to run the audio streaming server.
def init_stream_audio(port, device_index: int, server_ready_event):

    app = Flask(__name__)

    @app.route("/audio")
    def audio():
        return Response(sound_stream(device_index))

    @app.route("/")
    def index():
        """Video streaming home page."""
        return render_template("index.html")

    print(f"Audio streaming started at http://localhost:{port}/audio")

    # Server is about to start, signal the main thread
    server_ready_event.set()

    app.run(debug=False, threaded=True, port=port)

    # Finds and returns information about the preferred audio host API.


def start_audio_server(port, device_index: int):
    server_ready_event = threading.Event()
    stream_thread = threading.Thread(
        target=init_stream_audio, args=(port, device_index, server_ready_event)
    )

    stream_thread.daemon = True
    stream_thread.start()

    print("waiting the server run")
    p = pyaudio.PyAudio()

    # Wait here until the event is set, indicating the server is ready
    server_ready_event.wait()

    stream_url = f"http://localhost:{port}/audio"
    print(f"Audio stream server started on port {port}")

    return stream_url


# Finds and returns information about the preferred audio host API.
def get_api_info(p: pyaudio.PyAudio):
    PREFERRED_HOST_API_NAME = "Windows WASAPI"
    api_info, api_index = None, 0
    for i in range(p.get_host_api_count()):
        current_api_info = p.get_host_api_info_by_index(i)
        if i == 0:
            api_info = current_api_info
        else:
            if current_api_info["name"] == PREFERRED_HOST_API_NAME:
                api_info, api_index = current_api_info, i
                break
    return api_info, api_index


# Lists audio input devices available on the system.
def list_audio_devices(p: pyaudio.PyAudio):

    PREFERRED_HOST_API_NAME = "Windows WASAPI"
    devices = []
    api_info, api_index = get_api_info(p)
    api_name = api_info["name"]
    if api_name != PREFERRED_HOST_API_NAME:
        print(
            f'[WARNING] "{PREFERRED_HOST_API_NAME}" not available on this system, '
            f'going with "{api_name}" instead'
        )

    numdevices = api_info.get("deviceCount")
    for i in range(numdevices):
        dev_info = p.get_device_info_by_host_api_device_index(api_index, i)
        if dev_info.get("maxInputChannels") > 0:
            entry = (dev_info.get("name"), dev_info.get("index"))
            devices.append(entry)
    return devices


# Lists audio output devices available on the system.
def list_audio_output_devices(p: pyaudio.PyAudio):

    PREFERRED_HOST_API_NAME = "Windows WASAPI"
    devices = []
    api_info, api_index = get_api_info(p)
    api_name = api_info["name"]
    if api_name != PREFERRED_HOST_API_NAME:
        print(
            f'[WARNING] "{PREFERRED_HOST_API_NAME}" not available on this system, '
            f'going with "{api_name}" instead'
        )

    numdevices = api_info.get("deviceCount")
    for i in range(numdevices):
        dev_info = p.get_device_info_by_host_api_device_index(api_index, i)
        if dev_info.get("maxOutputChannels") > 0:
            devices.append(dev_info.get("name"))
    return devices


# Interactively allows the user to select an audio input device.
def select_input_device():

    p = pyaudio.PyAudio()
    device_list = list_audio_devices(p)
    for i, device in enumerate(device_list):
        print(f"{i + 1}. {device}")

    selected_device_index = None
    while True:
        try:
            selected_device_index = int(
                input("Please select an input device by entering its index: ")
            )
            if selected_device_index < 1 or selected_device_index > len(device_list):
                raise ValueError("Invalid index. Please enter a valid index.")
            break
        except ValueError as ve:
            print(ve)

    return (
        selected_device_index - 1
    )  # Adjusting index to match Python's zero-based indexing


# Returns the index of an audio device by its name.
def get_audio_device_index(device_name, p):
    for i in range(p.get_device_count()):
        dev_info = p.get_device_info_by_index(i)
        if dev_info["name"] == device_name:
            return i
    return None


# Returns the index of an audio input device by its name.
def get_input_device_index(device_name, audio):
    input_devices = list_audio_devices(audio)

    n = 0

    for device in input_devices:
        if device == device_name:
            return n
        n += 1

    return 0


# Returns the index of an audio output device by its name.
def get_output_device_index(device_name, audio):
    input_devices = list_audio_output_devices(audio)

    n = 0

    for device in input_devices:
        if device == device_name:
            return n
        n += 1

    return 0


# Lists input devices using the sounddevice library.
def list_input_devices_sd():
    devices = sd.query_devices()
    input_devices = []
    for device in devices:
        if device["max_input_channels"] > 0:
            input_devices.append(device["name"])
    return input_devices


# Finds and returns the index of a device by its name using the sounddevice library.
def find_device_index_sd(device_name):
    devices = sd.query_devices()
    for i, dev in enumerate(devices):
        if dev["name"] == device_name:
            return i
    return None
