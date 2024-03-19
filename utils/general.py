import json
from tkinter import messagebox
import sys
import os


def load_settings():
    try:
        with open("settings.json", "r") as json_file:
            settings = json.load(json_file)
    except FileNotFoundError:
        # Default settings if the file does not exist
        settings = {
            "audio_output": "",
            "audio_input": "",
            "input_device": 0,
            "output_device": 0,
            "port": "Auto",
        }
        # Write the default settings to a new file
        with open("settings.json", "w") as json_file:
            json.dump(settings, json_file, indent=4)
    return settings


def center_window(window):
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2)
    window.geometry("{}x{}+{}+{}".format(width, height, x, y))


def restart_application():
    """Restarts the current program, with file objects and descriptors cleanup"""
    try:
        # Attempt to restart the program using sys.executable and os.execl for a clean restart
        os.execl(sys.executable, sys.executable, *sys.argv)
    except Exception as e:
        # Log the exception or handle it as per your requirements
        print(f"Error restarting application: {e}")


# Opens the documenation.pdf file
def open_documentation(path):

    absolute_documentation_path = os.path.abspath(path)

    if sys.platform == "win32":
        os.startfile(absolute_documentation_path)


# Basically exits..
def exit_app(root):
    root.destroy()
