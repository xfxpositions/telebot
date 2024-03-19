# Initializes transcription and starts audio stream
from utils.transcription import start_audio_server, init_live_transcription, init_deepgram
import tkinter as tk
from threading import Event
from utils.settings import Settings


# Initialize the toggle event and transcription toggle function at a global scope
toggle_event = Event()
toggle_transcription = None

transcription_running = False
first_run = True

# Initialize deepgram client
deepgram = init_deepgram()

def init_transcription(deepgram, settings: Settings, transcription_text):
    global toggle_event, toggle_transcription
    # Only initialize once
    if toggle_transcription is None:
        # Start audio stream
        audio_stream_url = start_audio_server(
            port=settings.port,
            device_index=settings.input_device_index,
        )
        toggle_transcription = init_live_transcription(
            deepgram,
            stream_url=audio_stream_url,
            language="tr",
            textbox=transcription_text,
            toggle_event=toggle_event,
        )


# Starts or stops transcription based on current state
def start_transcription(transcription_text: tk.Text, start_stop_button: tk.Button, settings):
    global transcription_running, first_run, toggle_event
    # clear the transcription text
    transcription_text.delete("1.0", tk.END)

    if first_run:
        init_transcription(deepgram, settings, transcription_text)
        first_run = False

    # Toggle the transcription state
    toggle_transcription()

    # Update the transcription running state and button text
    transcription_running = not transcription_running
    start_stop_button.config(
        text="Stop Transcription" if transcription_running else "Start Transcription"
    )


def setup_transcription_frame(root, settings):

    # Transcription frame setup
    transcription_frame = tk.LabelFrame(root, text="Transcription:")
    transcription_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    # Conversation textbox setup
    transcription_text = tk.Text(transcription_frame, height=10, width=40)
    transcription_text.insert(
        tk.END,
        "Merhabalar, ben Mahmut Yazılımdan arıyorum.\nBilgisayarımda Logo ERP vardı fakat bugün giriş yapamıyorum. Bana yardımcı olur musunuz?",
    )
    transcription_text.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
    transcription_frame.grid_rowconfigure(0, weight=1)
    transcription_frame.grid_columnconfigure(0, weight=1)

    # Position buttons appropriately
    start_stop_button = tk.Button(
        transcription_frame, text="Start Transcription", command=lambda: start_transcription(transcription_text, start_stop_button, settings)
    )
    start_stop_button.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

    return transcription_text

