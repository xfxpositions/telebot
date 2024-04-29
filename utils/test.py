import tkinter as tk
from tkinter import ttk


class CredentialsWindow:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Credentials Setup")

        self.deepgram_api_key = tk.StringVar()
        self.openai_configs = []

        self.create_widgets()

    def create_widgets(self):
        # Deepgram API Key
        deepgram_label = ttk.Label(self.window, text="Deepgram API Key:")
        deepgram_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        deepgram_entry = ttk.Entry(self.window, textvariable=self.deepgram_api_key)
        deepgram_entry.grid(row=0, column=1, padx=5, pady=5)

        # OpenAI Configurations
        openai_label = ttk.Label(self.window, text="OpenAI Configurations:")
        openai_label.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)

        self.openai_combobox = ttk.Combobox(self.window, values=self.openai_configs)
        self.openai_combobox.grid(row=1, column=1, padx=5, pady=5)
        self.openai_combobox.bind(
            "<<ComboboxSelected>>", self.on_openai_config_selected
        )

        add_config_button = ttk.Button(
            self.window, text="Add Config", command=self.add_openai_config
        )
        add_config_button.grid(row=2, column=0, padx=5, pady=5)

        edit_config_button = ttk.Button(
            self.window, text="Edit Config", command=self.edit_openai_config
        )
        edit_config_button.grid(row=2, column=1, padx=5, pady=5)

        save_button = ttk.Button(
            self.window, text="Save", command=self.save_credentials
        )
        save_button.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

    def on_openai_config_selected(self, event):
        selected_config = self.openai_combobox.get()
        # Handle the selected OpenAI configuration
        print(f"Selected OpenAI Config: {selected_config}")

    def add_openai_config(self):
        config_window = tk.Toplevel(self.window)
        config_window.title("Add OpenAI Config")

        base_url_label = ttk.Label(config_window, text="Base URL:")
        base_url_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        base_url_entry = ttk.Entry(config_window)
        base_url_entry.grid(row=0, column=1, padx=5, pady=5)

        search_key_label = ttk.Label(config_window, text="Search Key:")
        search_key_label.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        search_key_entry = ttk.Entry(config_window)
        search_key_entry.grid(row=1, column=1, padx=5, pady=5)

        api_key_label = ttk.Label(config_window, text="API Key:")
        api_key_label.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        api_key_entry = ttk.Entry(config_window)
        api_key_entry.grid(row=2, column=1, padx=5, pady=5)

        save_button = ttk.Button(
            config_window,
            text="Save",
            command=lambda: self.save_openai_config(
                base_url_entry.get(),
                search_key_entry.get(),
                api_key_entry.get(),
                config_window,
            ),
        )
        save_button.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

    def edit_openai_config(self):
        selected_config = self.openai_combobox.get()
        if selected_config:
            # Open a new window to edit the selected OpenAI configuration
            config_window = tk.Toplevel(self.window)
            config_window.title("Edit OpenAI Config")

            # Populate the window with the selected configuration details
            # and provide options to edit and save the changes

    def save_openai_config(self, base_url, search_key, api_key, config_window):
        config = {"base_url": base_url, "search_key": search_key, "api_key": api_key}
        self.openai_configs.append(config)
        self.openai_combobox["values"] = self.openai_configs
        config_window.destroy()

    def save_credentials(self):
        deepgram_api_key = self.deepgram_api_key.get()
        openai_configs = self.openai_configs

        # Save the credentials to a file or database
        print(f"Deepgram API Key: {deepgram_api_key}")
        print(f"OpenAI Configurations: {openai_configs}")

    def run(self):
        self.window.mainloop()


# Create and run the credentials window
credentials_window = CredentialsWindow()
credentials_window.run()
