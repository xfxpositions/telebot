import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from ui.buttons import setup_buttons
from ui.kbase import setup_kbase_frame
from ui.prompt import setup_prompt_frame
from ui.transcription import setup_transcription_frame
from utils.transcription import (
    init_deepgram,
)
from utils.general import (
    load_settings,
    center_window,
)
import os
from threading import Event
import pyaudio
from ui.menubar import setup_menubar
from ui.settings import *

# CONFIG
# -------------------------

# Setup pyaudio
audio = pyaudio.PyAudio()

# Create main window
root = tk.Tk()
root.title("Telebot")

# Set the size of the window
width = 970
height = 520

root.geometry(f"{width}x{height}")

# Configure the root to expand the content dynamically
root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)

# load settings
settings = load_settings()

# VARIABLES
# -------------------------


# Settings
selected_input_device_index = settings["input_device_index"]
selected_output_device_index = settings["output_device_index"]

selected_input_device_name = settings["input_device"]
selected_output_device_name = settings["output_device"]

audio_server_port = settings["port"]

# General variables
transcription_running = False
first_run = True

# Initialize deepgram client
deepgram = init_deepgram()

# Initialize the toggle event and transcription toggle function at a global scope
toggle_event = Event()
toggle_transcription = None

documentation_path = os.path.join("documentation", "documentation.pdf")


# COMPONENTS
# --------------------------

setup_transcription_frame(root)
setup_kbase_frame(root)
setup_prompt_frame(root)
setup_buttons(root, documentation_path=documentation_path, audio=audio)
setup_menubar(root)
center_window(root)

if __name__ == "__main__":
    root.mainloop()
