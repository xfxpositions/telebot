import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from utils import make_openai_request_with_question, list_audio_devices
import threading
import pyaudio

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

# FUNCTIONS
# -------------------------

# Prints the size of the root window every 500 milliseconds.
def print_size():
    print("Window Size: {}x{}".format(root.winfo_width(), root.winfo_height()))
    root.after(500, print_size)  # Schedule print_size to be called again after 500 milliseconds

# Clears the content of the transcription_text and error_message_text widgets.
def clear_text():
    transcription_text.delete("1.0", tk.END)
    error_message_text.delete("1.0", tk.END)

# Copies the content of the transcription_text widget to the clipboard.
def copy_text():
    root.clipboard_clear()
    selected_text = transcription_text.get("1.0", tk.END)
    root.clipboard_append(selected_text)

# Searches for the provided text in the knowledge base.
def search_kb():
    textbox = prompt_message_text
    
    # Get the text from textbox
    text = error_message_text.get("1.0", "end-1c")
    
    # Set search button text to sending 
    button_old_text = search_kb_button.cget("text")
    search_kb_button.config(text="Sending...")

    def background_task():
        response = make_openai_request_with_question(question=text)['prompt']
        
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

# Opens a settings window for configuring various options.
def open_settings_window():
    settings_window = tk.Toplevel(root)
    settings_window.title("Settings")
    settings_window.geometry("500x400")  # Adjust the size based on the content
    settings_window.grab_set()  # Makes the settings window modal

    content_frame = tk.Frame(settings_window)
    content_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

    settings_label = tk.Label(content_frame, text="Settings", font=("Arial", 14))
    settings_label.pack(pady=(0, 10))

    # AUDIO INPUT DEVICES SECTION
    audio_input_label = tk.Label(content_frame, text="Audio Input Devices:", font=("Arial", 10))
    audio_input_label.pack()

    audio_input_devices = ["Microphone 1", "Microphone 2", "Microphone 3"]  # Placeholder list
    selected_input_device = tk.StringVar(settings_window)
    selected_input_device.set(audio_input_devices[0])

    audio_input_menu = tk.OptionMenu(content_frame, selected_input_device, *audio_input_devices)
    audio_input_menu.pack(pady=(10, 20))

    # AUDIO OUTPUT DEVICES SECTION
    audio_output_label = tk.Label(content_frame, text="Audio Output Devices:", font=("Arial", 10))
    audio_output_label.pack()

    audio_output_devices = ["Speaker 1", "Speaker 2", "Speaker 3"]  # Placeholder list
    selected_output_device = tk.StringVar(settings_window)
    selected_output_device.set(audio_output_devices[0])

    audio_output_menu = tk.OptionMenu(content_frame, selected_output_device, *audio_output_devices)
    audio_output_menu.pack(pady=(10, 20))

    # ADVANCED SETTINGS SECTION
    advanced_settings_frame = tk.Frame(content_frame)
    advanced_settings_button = tk.Button(advanced_settings_frame, text="Show Advanced Settings", command=lambda: toggle_advanced_settings(advanced_settings, advanced_settings_button))
    advanced_settings_button.pack(fill=tk.X)
    advanced_settings_frame.pack(fill=tk.X, pady=(20, 0))

    advanced_settings = tk.Frame(content_frame)

    # Audio Server Port Section
    audio_server_port_label = tk.Label(advanced_settings, text="Audio Server Port:", font=("Arial", 10))
    audio_server_port_label.pack()

    port_frame = tk.Frame(advanced_settings)
    port_frame.pack(fill=tk.X)
    
    audio_server_port = tk.StringVar()
    audio_server_port_entry = tk.Entry(port_frame, textvariable=audio_server_port)
    audio_server_port_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)

    auto_port = tk.BooleanVar()
    auto_port_checkbox = tk.Checkbutton(port_frame, text="Auto", variable=auto_port, command=lambda: toggle_auto_port(audio_server_port_entry, auto_port))
    auto_port_checkbox.pack(side=tk.RIGHT)

    # Buttons Frame
    buttons_frame = tk.Frame(settings_window)
    buttons_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(0, 10))

    apply_button = tk.Button(buttons_frame, text="Apply", command=lambda: apply_settings(selected_input_device.get(), selected_output_device.get(), audio_server_port.get(), auto_port.get()))
    apply_button.pack(side=tk.RIGHT, padx=10)

    cancel_button = tk.Button(buttons_frame, text="Close", command=settings_window.destroy)
    cancel_button.pack(side=tk.RIGHT)

# Toggles the visibility of advanced settings.
def toggle_advanced_settings(frame, button):
    if frame.winfo_viewable():
        frame.pack_forget()
        button.config(text="Show Advanced Settings")
    else:
        frame.pack(fill=tk.X, pady=(10, 20))
        button.config(text="Hide Advanced Settings")

# Toggles the state of the audio server port entry based on auto selection.
def toggle_auto_port(entry, auto_var):
    if auto_var.get():
        entry.config(state='disabled')
    else:
        entry.config(state='normal')

# Applies the selected settings.
def apply_settings(input_device, output_device, port, auto_port):
    print("Selected audio input device:", input_device)
    print("Selected audio output device:", output_device)
    if auto_port:
        print("Audio server port: Auto")
    else:
        print("Audio server port:", port)
    # Here you would implement the actual settings application logic


# COMPONENTS
# --------------------------

# Conversation frame setup
transcription_frame = tk.LabelFrame(root, text="Transcription:")
transcription_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

# Conversation textbox setup
transcription_text = tk.Text(transcription_frame, height=10, width=40)
transcription_text.insert(tk.END, "Merhabalar, ben Mahmut Yazılımdan arıyorum.\nBilgisayarımda Logo ERP vardı fakat bugün giriş yapamıyorum. Bana yardımcı olur musunuz?")
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
prompt_message_text.insert(tk.END, "Sorununuz şu şundan kaynaklanmaktadır. Şöyle ve şöyle yaparak çözebilirsiniz.")
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
start_stop_button = tk.Button(transcription_frame, text="Start/Stop")
start_stop_button.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

clear_button = tk.Button(buttons_frame, text="Clear", command=clear_text)
copy_button = tk.Button(buttons_frame, text="Copy", command=copy_text)
clear_button.pack(side="left", padx=5, pady=5)
copy_button.pack(side="left", padx=5, pady=5)

search_kb_button = tk.Button(error_message_frame, text="Search in KB", command=search_kb)
search_kb_button.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

# Right-aligned buttons setup
help_button = tk.Button(right_buttons_frame, text="Help")
settings_button = tk.Button(right_buttons_frame, text="Settings", command=open_settings_window)
exit_button = tk.Button(right_buttons_frame, text="Exit App", command=root.destroy)
help_button.pack(side="left", padx=5, pady=5)
settings_button.pack(side="left", padx=5, pady=5)
exit_button.pack(side="left", padx=5, pady=5)

# Run the application
root.mainloop()
