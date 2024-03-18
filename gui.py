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


# Opens the documenation.pdf file
def open_documentation():
    documentation_path = os.path.join("documentation", "documentation.pdf")
    absolute_documentation_path = os.path.abspath(documentation_path)

    if sys.platform == "win32":
        os.startfile(absolute_documentation_path)


# Define a function to show information about the application
def show_about():
    # Create a new window for displaying about information
    about_window = tk.Toplevel(root)
    about_window.geometry("300x300")
    center_window(about_window)
    about_window.title("About")

    # Display application information
    tk.Label(about_window, text="Logo Telebot", font=("Arial", 16)).pack(pady=(10, 0))
    tk.Label(about_window, text="Version: 0.2", font=("Arial", 12)).pack(pady=10)
    tk.Label(
        about_window,
        text="Contributors:\n\nYusuf Karaca\nSinan Yalcinkaya\nBora Bulus",
        font=("Arial", 12),
    ).pack(pady=10)

    # Add a button to view the license
    view_license_btn = tk.Button(
        about_window, text="View License", command=open_license_file
    )
    view_license_btn.pack(pady=(5, 10))

    # Add a button to close the about window
    close_btn = tk.Button(about_window, text="Close", command=about_window.destroy)
    close_btn.pack(pady=5)


# Opens the license and shows in messagebox
def open_license_file():
    try:
        with open("LICENSE", "r") as file:
            license_text = file.read()
        messagebox.showinfo("License", license_text)
    except FileNotFoundError:
        messagebox.showerror("Error", "License file not found.")


# Basically exits..
def exit_app():
    root.destroy()


# Applies the selected settings.
def apply_settings(
    input_device_name, output_device_name, port, auto_port, settings_window
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
    root.clipboard_clear()
    selected_text = f"transcrioption: {transcription_text.get('1.0', tk.END)}, question: {error_message_text.get('1.0', tk.END)}, prompt: {prompt_message_text.get('1.0', tk.END)}"

    root.clipboard_append(selected_text)


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


# Opens a settings window for configuring various options.
def open_settings_window():
    load_settings()
    global selected_input_device_name, selected_output_device_name, audio_server_port

    selected_input_device_name = settings["input_device"]
    selected_output_device_name = settings["output_device"]
    audio_server_port = settings["port"]

    # Initialize the settings window
    settings_window = tk.Toplevel(root)
    settings_window.title("Settings")
    settings_window.geometry("500x400")
    settings_window.grab_set()

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


# COMPONENTS
# --------------------------

# Menubar

# Create a menubar
menubar = tk.Menu(root)

# File menu
menu_file = tk.Menu(menubar, tearoff=0)
menu_file.add_command(label="Exit", command=exit_app)
menubar.add_cascade(label="File", menu=menu_file)

# Settings menu with a submenu
menu_settings = tk.Menu(menubar, tearoff=0)
submenu_general_settings = tk.Menu(menu_settings, tearoff=0)
submenu_general_settings.add_command(label="General", command=open_settings_window)
menu_settings.add_cascade(label="Settings", menu=submenu_general_settings)
menubar.add_cascade(label="Settings", menu=menu_settings)

# Help menu
menu_help = tk.Menu(menubar, tearoff=0)
menu_help.add_command(label="About", command=show_about)
menu_help.add_command(label="Documentation", command=open_documentation)

menubar.add_cascade(label="Help", menu=menu_help)

# Display the menu
root.config(menu=menubar)

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
