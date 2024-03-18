import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from utils.transcription import (
    list_audio_devices,
    start_audio_server,
    init_deepgram,
    init_live_transcription,
    list_audio_output_devices,
)
from utils.kbase import make_openai_request_with_question
from utils.general import load_settings, center_window, restart_application
import os
import sys
import threading
from threading import Event
import pyaudio
import json
from ui import menubar
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

# FUNCTIONS
# -------------------------


# Initializes transcription and starts audio stream
def init_transcription():
    global toggle_transcription
    # Only initialize once
    if toggle_transcription is None:
        # Start audio stream
        audio_stream_url = start_audio_server(
            port=audio_server_port, device_index=selected_input_device_index
        )
        toggle_transcription = init_live_transcription(
            deepgram,
            stream_url=audio_stream_url,
            language="tr",
            textbox=transcription_text,
            toggle_event=toggle_event,
        )


# Starts or stops transcription based on current state
def start_transcription():
    global transcription_running, first_run

    # clear the transcription text
    transcription_text.delete("1.0", tk.END)

    if first_run:
        init_transcription()
        first_run = False

    # Toggle the transcription state
    toggle_transcription()

    # Update the transcription running state and button text
    transcription_running = not transcription_running
    start_stop_button.config(
        text="Stop Transcription" if transcription_running else "Start Transcription"
    )


# Prints the size of the root window every 500 milliseconds.
def print_size():
    print("Window Size: {}x{}".format(root.winfo_width(), root.winfo_height()))
    root.after(
        500, print_size
    )  # Schedule print_size to be called again after 500 milliseconds


# Clears the content of the transcription_text and error_message_text widgets.
def clear_text():
    transcription_text.delete("1.0", tk.END)
    error_message_text.delete("1.0", tk.END)
    prompt_message_text.delete("1.0", tk.END)


# Copies the content of the transcription_text widget to the clipboard.
def copy_text():
    # Get the selected text in prompt message
    selected_text = prompt_message_frame.selection_get()

    # Delete and copy to error message prompt
    error_message_text.delete(1.0, tk.END)
    error_message_text.insert(tk.END, selected_text)


# Searches for the provided text in the knowledge base.
def search_kb():
    # Clear the past prompt
    prompt_message_text.delete("1.0", tk.END)

    textbox = prompt_message_text

    # Get the text from textbox
    text = error_message_text.get("1.0", "end-1c")

    # Set search button text to sending
    button_old_text = search_kb_button.cget("text")
    search_kb_button.config(text="Sending...")

    def background_task():
        response = make_openai_request_with_question(question=text)["prompt"]

        # Update gui safely
        def update_gui():
            textbox.delete("1.0", "end")  # Clear previous text
            textbox.insert("1.0", response)
            search_kb_button.config(text=button_old_text)

        # Update gui in the main thread
        textbox.after(0, update_gui)

    # Run background thread
    thread = threading.Thread(target=background_task)
    thread.start()


# COMPONENTS
# --------------------------


# Conversation frame setup
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

# Error message frame setup
error_message_frame = tk.LabelFrame(root, text="Search")
error_message_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
root.grid_columnconfigure(1, weight=1)

# Error message textbox setup
error_message_text = tk.Text(error_message_frame, height=10, width=40)
error_message_text.insert(tk.END, "Lütfen sorunu yazınız..")
error_message_text.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
error_message_frame.grid_rowconfigure(0, weight=1)
error_message_frame.grid_columnconfigure(0, weight=1)

# Admin message frame setup
prompt_message_frame = tk.LabelFrame(root, text="Prompt")
prompt_message_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=0, sticky="nsew")

# Admin message textbox setup
prompt_message_text = tk.Text(prompt_message_frame, height=4, width=88)
prompt_message_text.insert(
    tk.END,
    "Sorununuz şu şundan kaynaklanmaktadır. Şöyle ve şöyle yaparak çözebilirsiniz.",
)
prompt_message_text.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
prompt_message_frame.grid_rowconfigure(0, weight=1)
prompt_message_frame.grid_columnconfigure(0, weight=1)

# Buttons frame setup for layout adjustment
buttons_frame = tk.Frame(root)
buttons_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
root.grid_rowconfigure(2, weight=0)  # Keep buttons row from expanding

right_buttons_frame = tk.Frame(buttons_frame)  # Frame for right-aligned buttons
right_buttons_frame.pack(side="right")  # Align to the right

# Position buttons appropriately
start_stop_button = tk.Button(
    transcription_frame, text="Start Transcription", command=start_transcription
)
start_stop_button.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

clear_button = tk.Button(buttons_frame, text="Clear", command=clear_text)
copy_button = tk.Button(buttons_frame, text="Copy", command=copy_text)
clear_button.pack(side="left", padx=5, pady=5)
copy_button.pack(side="left", padx=5, pady=5)

search_kb_button = tk.Button(
    error_message_frame, text="Search in KB", command=search_kb
)
search_kb_button.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

# Right-aligned buttons setup
help_button = tk.Button(right_buttons_frame, text="Help", command=open_documentation)
settings_button = tk.Button(
    right_buttons_frame, text="Settings", command=open_settings_window
)
exit_button = tk.Button(right_buttons_frame, text="Exit App", command=root.destroy)
help_button.pack(side="left", padx=5, pady=5)
settings_button.pack(side="left", padx=5, pady=5)
exit_button.pack(side="left", padx=5, pady=5)


# Center the window before start
center_window(root)

if __name__ == "__main__":
    root.mainloop()
