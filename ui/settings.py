import tkinter as tk
from tkinter import messagebox
import pyaudio
from utils.general import center_window, restart_application
from utils.settings import Settings
from utils.transcription import list_audio_devices, list_audio_output_devices

# Function to toggle the visibility of advanced settings
def toggle_advanced_settings(frame, button):
    if frame.winfo_viewable():
        frame.pack_forget()
        button.config(text="Show Advanced Settings")
    else:
        frame.pack(fill=tk.X, pady=(10, 20))
        button.config(text="Hide Advanced Settings")

# Function to toggle the state of the audio server port entry based on auto selection
def toggle_auto_port(entry, auto_var):
    if auto_var.get():
        entry.config(state="disabled")
    else:
        entry.config(state="normal")



# Function to open the settings window and configure various options
def open_settings_window(root):
    settings = Settings()  # Instantiate the Settings class

    # Fetching the list of audio input and output devices
    audio_input_devices = list_audio_devices()
    audio_output_devices = list_audio_output_devices()

    # Initialize the settings window
    settings_window = tk.Toplevel(root)
    settings_window.title("Settings")
    settings_window.geometry("500x400")
    settings_window.grab_set()
    settings_window.resizable(False, False)
    center_window(settings_window)

    # Preparing variables for the component setup
    selected_input_device = tk.StringVar(settings_window, value=settings.input_device)
    selected_output_device = tk.StringVar(settings_window, value=settings.output_device)
    audio_server_port_value = tk.StringVar(settings_window, value=settings.port)
    selected_input_device_info = tk.StringVar(settings_window, value=settings.input_device)
    selected_output_device_info = tk.StringVar(settings_window, value=settings.output_device)
    auto_port = tk.BooleanVar(value=settings.port == "Auto")

    # Callback functions
    def on_input_device_change(*args):
        device_info = selected_input_device_info.get()
        device_name, device_index = device_info.rsplit(":", 1)
        settings.input_device = device_name.strip()
        settings.input_device_index = int(device_index.strip())
        print(f"Input Device changed to: {settings.input_device} with index {settings.input_device_index}")

    def on_output_device_change(*args):
        device_info = selected_output_device_info.get()
        device_name, device_index = device_info.rsplit(":", 1)
        settings.output_device = device_name.strip()
        settings.output_device_index = int(device_index.strip())
        print(f"Output Device changed to: {settings.output_device} with index {settings.output_device_index}")

    def on_port_value_change(*args):
        new_value = audio_server_port_value.get()
        print(f"Server port changed to: {new_value}")
        # Update your settings object here
        settings.port = new_value

    def on_auto_port_change(*args):
        is_auto = auto_port.get()
        print(f"Auto Port changed to: {is_auto}")
        # Update your settings object here
        # For example, if auto, set port to "Auto", otherwise keep or set a specific port
        settings.port = "Auto" if is_auto else audio_server_port_value.get()

    # Attach the trace_add method to variables
    selected_input_device.trace_add("write", on_input_device_change)
    selected_output_device.trace_add("write", on_output_device_change)
    selected_input_device_info.trace_add("write", on_input_device_change)
    selected_output_device_info.trace_add("write", on_output_device_change)
    audio_server_port_value.trace_add("write", on_port_value_change)
    auto_port.trace_add("write", on_auto_port_change)


    # Creating UI components
    # Settings label
    content_frame = tk.Frame(settings_window)
    settings_label = tk.Label(content_frame, text="Settings", font=("Arial", 14))

    # Audio Input Devices Section
    audio_input_label = tk.Label(content_frame, text="Audio Input Devices:", font=("Arial", 10))
    audio_input_menu = tk.OptionMenu(content_frame, selected_input_device_info, *["{}: {}".format(device[0], device[1]) for device in audio_input_devices])



    # Audio Output Devices Section
    audio_output_label = tk.Label(content_frame, text="Audio Output Devices:", font=("Arial", 10))
    audio_output_menu = tk.OptionMenu(content_frame, selected_output_device_info, *["{}: {}".format(device[0], device[1]) for device in audio_output_devices])

    # Advanced Settings Section
    advanced_settings_frame = tk.Frame(content_frame)
    advanced_settings_button = tk.Button(advanced_settings_frame, text="Show Advanced Settings",
                                         command=lambda: toggle_advanced_settings(advanced_settings, advanced_settings_button))
    advanced_settings = tk.Frame(content_frame)
    audio_server_port_label = tk.Label(advanced_settings, text="Audio Server Port:", font=("Arial", 10))
    port_frame = tk.Frame(advanced_settings)
    audio_server_port_entry = tk.Entry(port_frame, textvariable=audio_server_port_value)
    auto_port_checkbox = tk.Checkbutton(port_frame, text="Auto", variable=auto_port, command=lambda: toggle_auto_port(audio_server_port_entry, auto_port))

    # Buttons Frame
    buttons_frame = tk.Frame(settings_window)
    apply_button = tk.Button(buttons_frame, text="Apply", command=lambda: settings.apply_settings(settings_window, restart_application))
    cancel_button = tk.Button(buttons_frame, text="Close", command=settings_window.destroy)

    # Packing UI components
    content_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
    settings_label.pack(pady=(0, 10))
    audio_input_label.pack()
    audio_input_menu.pack(pady=(10, 20))
    audio_output_label.pack()
    audio_output_menu.pack(pady=(10, 20))
    advanced_settings_frame.pack(fill=tk.X, pady=(20, 0))
    advanced_settings_button.pack(fill=tk.X)
    audio_server_port_label.pack()
    port_frame.pack(fill=tk.X)
    audio_server_port_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
    auto_port_checkbox.pack(side=tk.RIGHT)
    buttons_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(0, 10))
    apply_button.pack(side=tk.RIGHT, padx=10)
    cancel_button.pack(side=tk.RIGHT)

    print(f"Server port: {audio_server_port_value.get()}")
