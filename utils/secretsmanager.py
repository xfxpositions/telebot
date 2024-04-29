import tkinter as tk
from tkinter import ttk
from utils.cryptomanager import CryptoManager
from utils.general import center_window
import json
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding


class OpenAIConfig:
    def __init__(self, name, apiKey, url, embeddingKey, searchKey, indexname):
        self.name = name
        self.apiKey = apiKey
        self.url = url
        self.embeddingKey = embeddingKey
        self.searchKey = searchKey
        self.indexname = indexname


class SecretsManager:
    def __init__(self):
        # Initialize secrets
        self.crypto_manager = CryptoManager()  # Include CryptoManager instance

        self.deepgram_api_key = ""
        self.openai_configs = []

        # Default settings JSON filename
        self.settings_filename = "secrets.json"

        # Load settings from JSON file at startup
        self.load_settings(self.settings_filename)

    def update_deepgram_api_key(self, new_api_key):
        # Update Deepgram API key
        self.deepgram_api_key = new_api_key
        # Perform additional actions if needed, such as saving to a file or database
        print("Deepgram API key updated:", self.deepgram_api_key)

    def add_openai_config(self, config):
        # Add OpenAI configuration
        self.openai_configs.append(config)
        print("OpenAI configuration added:", config.name)

    def update_secrets(self, new_deepgram_api_key, openai_config_index):
        # Update Deepgram API key
        self.update_deepgram_api_key(new_deepgram_api_key)

        # Update selected OpenAI config
        selected_config = self.openai_configs[openai_config_index]
        print(
            "Updated OpenAI configuration:",
            selected_config.name,
            selected_config.apiKey,
        )

        # Save settings to file after updating
        self.to_json(self.settings_filename)

    def to_json(self, file_path):
        # Serialize the SecretsManager instance to JSON
        data = {
            "deepgram_api_key": self.deepgram_api_key,
            "openai_configs": [vars(config) for config in self.openai_configs],
        }
        # Write to JSON file
        encrypted_data = self.crypto_manager.encrypt_message(json.dumps(data))
        with open(file_path, "w") as file:
            file.write(encrypted_data)

    def load_settings(self, file_path):
        # Decrypt the JSON file and load settings
        try:
            with open(file_path, "rb") as file:
                encrypted_data = file.read()
                # Decrypt the data directly without encoding, as it's already in byte form
                decrypted_data = self.crypto_manager.decrypt_message(encrypted_data)
                data = json.loads(decrypted_data)
                self.deepgram_api_key = data["deepgram_api_key"]
                self.openai_configs = [
                    OpenAIConfig(**config_data)
                    for config_data in data["openai_configs"]
                ]
        except FileNotFoundError:
            print("Settings file not found. Creating default settings.")
            # Create default settings
            self.create_default_settings()
            # Save default settings to file
            self.to_json(file_path)

    def create_default_settings(self):
        # Create default settings
        self.deepgram_api_key = "default_api_key"
        self.openai_configs = [
            OpenAIConfig(
                "Default OpenAI Config",
                "default_apiKey",
                "default_url",
                "default_embeddingKey",
                "default_searchKey",
                "default_indexname",
            )
        ]

    def edit_openai_config(self, config_index):
        # Function to create a window for editing OpenAI config fields
        def save_changes():
            # Update OpenAI config fields with new values from entry fields
            for i, attribute in enumerate(attributes):
                setattr(selected_config, attribute, entry_fields[i].get())
            print("Changes saved for", selected_config.name)

            # Close the edit window
            edit_window.destroy()

            # Save settings to file after editing
            self.to_json(self.settings_filename)

        # Get the selected OpenAI config
        selected_config = self.openai_configs[config_index]

        # Create a window for editing OpenAI config fields
        edit_window = tk.Toplevel()
        edit_window.title("Edit OpenAI Config")
        edit_window.geometry("400x300")
        center_window(edit_window)

        # Labels and entry fields for each attribute of the selected OpenAI config
        attributes = vars(OpenAIConfig("", "", "", "", "", ""))

        entry_fields = []

        for attribute in attributes:
            label = ttk.Label(edit_window, text=attribute.capitalize() + ":")
            label.pack()
            entry_field = ttk.Entry(edit_window, width=30)
            entry_field.insert(0, getattr(selected_config, attribute))
            entry_field.pack()
            entry_fields.append(entry_field)

        # Button to save changes
        save_button = ttk.Button(edit_window, text="Save Changes", command=save_changes)
        save_button.pack()
