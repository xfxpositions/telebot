import tkinter as tk
from tkinter import messagebox
import json
import pyaudio
from utils.general import restart_application
from utils.transcription import list_audio_devices, list_audio_output_devices

class Settings:
    def __init__(self):
        self.input_device = ""
        self.output_device = ""
        self.input_device_index = None
        self.output_device_index = None
        self.port = "Auto"
        self.openai_config_path = "openai_config.json"
        self.documentation_path = "documenatation/documentation.pdf"
        self.first_run = True

        self.openai_index = "indexbuluterpdys"

        self.load_settings()

    def load_settings(self):
        try:
            with open("settings.json", "r") as json_file:
                settings = json.load(json_file)
                self.input_device = settings.get("input_device", "")
                self.output_device = settings.get("output_device", "")
                self.input_device_index = settings.get("input_device_index")
                self.output_device_index = settings.get("output_device_index")

                self.openai_config_path = settings.get("openai_config_path")
                self.openai_index = settings.get("openai_index")

                self.documentation_path = settings.get("documentation_path")
                self.first_run = settings.get("first_run")

                self.port = settings.get("port", "Auto")
        except FileNotFoundError:
            print("settings.json not found")
            self.save_settings()  # Save the default settings if the file does not exist

    def save_settings(self):
        settings = {
            "input_device": self.input_device,
            "output_device": self.output_device,
            "input_device_index": self.input_device_index,
            "output_device_index": self.output_device_index,
            "first_run": self.first_run,

            "openai_config_path": self.openai_config_path,
            "openai_index": self.openai_index,

            "documentation_path": self.documentation_path,

            "port": self.port,
        }
        with open("settings.json", "w") as json_file:
            json.dump(settings, json_file, indent=4)

    def apply_settings(self, settings_window, restart_application_callback):
        old_settings = Settings()

        input_devices = list_audio_devices()
        output_devices = list_audio_output_devices()

        selected_input_device_info = next((device for device in input_devices if device[0] == self.input_device), None)
        self.input_device_index = selected_input_device_info[1] if selected_input_device_info else None
        
        selected_output_device_info = next((device for device in output_devices if device[0] == self.output_device), None)
        self.output_device_index = selected_output_device_info[1] if selected_output_device_info else None
        
        self.save_settings()

        need_restart = False

        if old_settings.output_device_index!= self.output_device_index:
            need_restart = True
        if old_settings.input_device_index != self.input_device_index:
            need_restart = True

        print("settings saved.")

        # Assume you've updated this logic as per your actual conditions for restart requirement
        
        if need_restart:
            user_choice = messagebox.askyesno(
                "Restart Required",
                "We have to restart the application for the changes to take effect. Do you want to restart now?",
            )
            if user_choice:
                restart_application_callback()
            else:
                settings_window.destroy()
        else:
            settings_window.destroy()

    # You might need additional methods to update individual settings, like device names or port,
    # before calling apply_settings(). These methods can modify the class attributes directly.

