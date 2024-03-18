import tkinter as tk
from utils.general import center_window, load_settings, restart_application
from utils.transcription import list_audio_devices, list_audio_output_devices
from tkinter import messagebox
import json
import pyaudio


# Applies the selected settings.
def apply_settings(
    input_device_name, output_device_name, port, auto_port, settings_window, audio
):
    global selected_input_device_index, selected_output_device_index, selected_input_device_name, selected_output_device_name, audio_server_port

    # Retrieve the full device information lists again to find the selected devices' indices
    input_devices = list_audio_devices(p=audio)
    output_devices = list_audio_output_devices(p=audio)

    # Find the index for the selected input device
    selected_input_device_info = next(
        (device for device in input_devices if device[0] == input_device_name), None
    )
    selected_input_device_index = (
        selected_input_device_info[1] if selected_input_device_info else None
    )

    # Find the index for the selected output device
    selected_output_device_info = next(
        (device for device in output_devices if device[0] == output_device_name), None
    )
    selected_output_device_index = (
        selected_output_device_info[1] if selected_output_device_info else None
    )

    new_port = "Auto" if auto_port else port
    settings_changed = (
        input_device_name != selected_input_device_name
        or output_device_name != selected_output_device_name
        or new_port != audio_server_port
    )

    need_restart = settings_changed

    selected_input_device_name = input_device_name
    selected_output_device_name = output_device_name
    audio_server_port = new_port

    settings = {
        "input_device": selected_input_device_name,
        "input_device_index": selected_input_device_index,
        "output_device": selected_output_device_name,
        "output_device_index": selected_output_device_index,
        "port": new_port,
    }

    # Saving to a JSON file
    with open("settings.json", "w") as json_file:
        json.dump(settings, json_file, indent=4)

    # Here you would implement the actual settings application logic
    print(json.dumps(settings, indent=4))

    if need_restart:
        # Now, prompt the user to restart the application for changes to take effect
        user_choice = messagebox.askyesno(
            "Restart Required",
            "We have to restart the application for the changes to take effect. Do you want to restart now?",
        )

        if user_choice:  # If the user clicks 'Yes', restart the application
            restart_application()
        else:  # If the user clicks 'No', just close the settings window
            settings_window.destroy()
    else:
        # Close the settings window if there's no need to restart
        settings_window.destroy()


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
        entry.config(state="disabled")
    else:
        entry.config(state="normal")


# Opens a settings window for configuring various options.
def open_settings_window(root):
    audio = pyaudio.PyAudio()
    global selected_input_device_name, selected_output_device_name, audio_server_port

    settings = load_settings()

    selected_input_device_index = settings["input_device_index"]
    selected_output_device_index = settings["output_device_index"]

    selected_input_device_name = settings["input_device"]
    selected_output_device_name = settings["output_device"]

    audio_server_port = settings["port"]

    # Initialize the settings window
    settings_window = tk.Toplevel(root)
    settings_window.title("Settings")
    settings_window.geometry("500x400")
    settings_window.grab_set()
    settings_window.resizable(False, False)
    center_window(settings_window)
    content_frame = tk.Frame(settings_window)
    content_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

    settings_label = tk.Label(content_frame, text="Settings", font=("Arial", 14))
    settings_label.pack(pady=(0, 10))

    # AUDIO INPUT DEVICES SECTION
    audio_input_label = tk.Label(
        content_frame, text="Audio Input Devices:", font=("Arial", 10)
    )
    audio_input_label.pack()

    audio_input_devices = list_audio_devices(p=audio)

    selected_input_device = tk.StringVar(settings_window)
    selected_input_device.set(selected_input_device_name)

    audio_input_menu = tk.OptionMenu(
        content_frame,
        selected_input_device,
        *[device[0] for device in audio_input_devices],
    )
    audio_input_menu.pack(pady=(10, 20))

    # AUDIO OUTPUT DEVICES SECTION (Assuming similar function `list_audio_output_devices` returns the same format)
    audio_output_label = tk.Label(
        content_frame, text="Audio Output Devices:", font=("Arial", 10)
    )
    audio_output_label.pack()

    audio_output_devices = list_audio_output_devices(p=audio)

    selected_output_device = tk.StringVar(settings_window)
    selected_output_device.set(selected_output_device_name)

    audio_output_menu = tk.OptionMenu(
        content_frame,
        selected_output_device,
        *[device[0] for device in audio_output_devices],
    )
    audio_output_menu.pack(pady=(10, 20))

    # ADVANCED SETTINGS SECTION
    advanced_settings_frame = tk.Frame(content_frame)
    advanced_settings_button = tk.Button(
        advanced_settings_frame,
        text="Show Advanced Settings",
        command=lambda: toggle_advanced_settings(
            advanced_settings, advanced_settings_button
        ),
    )
    advanced_settings_button.pack(fill=tk.X)
    advanced_settings_frame.pack(fill=tk.X, pady=(20, 0))

    advanced_settings = tk.Frame(content_frame)

    # Audio Server Port Section
    audio_server_port_label = tk.Label(
        advanced_settings, text="Audio Server Port:", font=("Arial", 10)
    )
    audio_server_port_label.pack()

    port_frame = tk.Frame(advanced_settings)
    port_frame.pack(fill=tk.X)

    audio_server_port_value = tk.StringVar(
        settings_window, value=settings.get("port", "Auto")
    )
    print(f"server port: {audio_server_port_value.get()}")
    audio_server_port_entry = tk.Entry(port_frame, textvariable=audio_server_port_value)
    audio_server_port_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)

    auto_port = tk.BooleanVar()
    auto_port_checkbox = tk.Checkbutton(
        port_frame,
        text="Auto",
        variable=auto_port,
        command=lambda: toggle_auto_port(audio_server_port_entry, auto_port),
    )
    auto_port_checkbox.pack(side=tk.RIGHT)

    # Buttons Frame
    buttons_frame = tk.Frame(settings_window)
    buttons_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(0, 10))

    apply_button = tk.Button(
        buttons_frame,
        text="Apply",
        command=lambda: apply_settings(
            selected_input_device.get(),
            selected_output_device.get(),
            audio_server_port_entry.get(),
            auto_port.get(),
            settings_window,
        ),
    )
    apply_button.pack(side=tk.RIGHT, padx=10)

    cancel_button = tk.Button(
        buttons_frame, text="Close", command=settings_window.destroy
    )
    cancel_button.pack(side=tk.RIGHT)
