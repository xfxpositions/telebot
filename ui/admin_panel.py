import tkinter as tk
from tkinter import ttk
from utils.general import center_window
from utils.secretsmanager import OpenAIConfig, SecretsManager
from tkinter import messagebox  # Import messagebox for error handling
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


def start_watcher(file_path, update_func):
    class SettingsChangeHandler(FileSystemEventHandler):
        def on_modified(self, event):
            if event.src_path == file_path:
                update_func()

    event_handler = SettingsChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path=file_path, recursive=False)
    observer.start()


def update_combobox(secrets_manager, combobox):
    secrets_manager.load_secrets()  # Reload secrets from file
    openai_config_names = [config.name for config in secrets_manager.openai_configs]
    combobox["values"] = openai_config_names
    if openai_config_names:
        combobox.current(0)
    else:
        combobox.set("")  # Clear combobox if no items left


def open_admin_panel_window(root: tk.Tk):

    # Track unsaved changes
    unsaved_changes = False

    admin_panel = tk.Toplevel(root)
    admin_panel.title("Admin Panel")
    admin_panel.geometry("600x500")  # Adjusted for better spacing
    center_window(admin_panel)

    secrets_manager = SecretsManager()

    # Frame for API configurations
    config_frame = ttk.Frame(admin_panel, padding="10 10 10 10")
    config_frame.pack(fill="x", expand=True)

    # Labels and Entries
    ttk.Label(config_frame, text="Welcome to the Admin Panel").pack(pady=10)

    ttk.Label(config_frame, text="Deepgram API Key:").pack(anchor="w")
    deepgram_api_key_entry = ttk.Entry(config_frame)
    deepgram_api_key_entry.insert(0, secrets_manager.deepgram_api_key)
    deepgram_api_key_entry.pack(fill="x", padx=5, pady=5)

    # Combobox for selecting OpenAI configurations
    ttk.Label(config_frame, text="OpenAI Configs:").pack(anchor="w")
    openai_config_combobox = ttk.Combobox(config_frame, state="readonly")
    openai_config_names = [config.name for config in secrets_manager.openai_configs]
    openai_config_combobox["values"] = openai_config_names
    openai_config_combobox.pack(fill="x", padx=5, pady=5)
    if openai_config_names:
        openai_config_combobox.current(0)

    # Frame for buttons
    button_frame = ttk.Frame(admin_panel, padding="10 10 10 10")
    button_frame.pack(fill="x", expand=True)

    # Initialize watchdog
    start_watcher(
        secrets_manager.settings_filename,
        lambda: update_combobox(secrets_manager, openai_config_combobox),
    )

    # Buttons
    ttk.Button(
        button_frame,
        text="Add New OpenAI Config",
        command=lambda: add_new_openai_config(),
    ).pack(side="left", expand=True, padx=5, pady=5)
    update_secrets_button = ttk.Button(
        button_frame,
        text="Update Secrets",
        command=lambda: update_secrets(),
    )
    update_secrets_button.pack(side="left", expand=True, padx=5, pady=5)

    # Button for deleting OpenAI Config
    delete_button = ttk.Button(
        button_frame,
        text="Delete OpenAI Config",
        command=lambda: delete_openai_config(),
    )
    delete_button.pack(side="left", expand=True, padx=5, pady=5)

    # Button for deleting OpenAI Config
    edit_button = ttk.Button(
        button_frame,
        text="Edit OpenAI Config",
        command=lambda: edit_selected_openai_config(),
    )
    edit_button.pack(side="left", expand=True, padx=5, pady=5)

    # Control Buttons
    control_frame = ttk.Frame(admin_panel, padding="10")
    control_frame.pack(fill="x", side="bottom", anchor="e")

    apply_button = ttk.Button(
        control_frame, text="Apply", command=lambda: update_secrets()
    )
    apply_button.pack(side="right", padx=5, pady=5)  # Changed side to "right"

    exit_button = ttk.Button(control_frame, text="Exit", command=lambda: exit_prompt())
    exit_button.pack(side="right", padx=5, pady=5)  # Changed side to "right"

    def apply_changes():
        # Function to apply changes
        print("Apply changes")

    def add_new_openai_config():
        new_config = OpenAIConfig("New Config", "", "", "", "", "")
        edit_openai_config(
            new_config, add=True
        )  # Pass new config to edit function with add flag

    def exit_prompt():
        if unsaved_changes:
            if messagebox.askyesno(
                "Unsaved Changes",
                "You have unsaved changes. Do you still want to exit?",
            ):
                admin_panel.destroy()
        else:
            admin_panel.destroy()

    def edit_selected_openai_config():
        current_index = openai_config_combobox.current()
        if current_index == -1:  # No selection made
            messagebox.showerror("Error", "No configuration selected to edit.")
        else:
            selected_config = secrets_manager.openai_configs[current_index]
            edit_openai_config(selected_config)

    def edit_openai_config(config, add=False):
        # Create a window for editing OpenAI config fields
        edit_window = tk.Toplevel(admin_panel)
        edit_window.title("Edit OpenAI Config")
        edit_window.geometry("500x400")
        edit_window.resizable(False, False)
        center_window(edit_window)

        entry_fields = {}
        for attribute in vars(config):
            label = ttk.Label(edit_window, text=attribute.capitalize() + ":")
            label.pack()
            entry = ttk.Entry(edit_window, width=30)
            entry.insert(0, getattr(config, attribute))
            entry.pack()
            entry_fields[attribute] = entry

        def save_changes():
            for attribute, entry in entry_fields.items():
                setattr(config, attribute, entry.get())
            print("Changes saved for", config.name)
            if add:
                secrets_manager.add_openai_config(config)
                update_combobox()
            edit_window.destroy()

        save_button = ttk.Button(edit_window, text="Save Changes", command=save_changes)
        save_button.pack()

    def delete_openai_config():
        current_index = openai_config_combobox.current()
        if current_index == -1:  # No selection made
            messagebox.showerror("Error", "No configuration selected to delete.")
            return

        def confirm_deletion():
            if name_entry.get() == secrets_manager.openai_configs[current_index].name:
                # Proceed with deletion
                selected_config = secrets_manager.openai_configs.pop(current_index)
                messagebox.showinfo(
                    "Deleted",
                    f"Configuration '{selected_config.name}' deleted successfully.",
                )
                # Update the combobox values
                update_combobox()
                confirm_window.destroy()
            else:
                messagebox.showerror("Error", "Configuration name does not match.")

        # Confirmation window
        confirm_window = tk.Toplevel(admin_panel)
        confirm_window.title("Confirm Deletion")
        confirm_window.geometry("500x150")
        confirm_window.resizable(False, False)
        center_window(confirm_window)
        name = secrets_manager.openai_configs[current_index].name
        ttk.Label(
            confirm_window,
            text=f'Type "{name}" of the configuration to confirm deletion:',
        ).pack(pady=5)
        name_entry = ttk.Entry(confirm_window)
        name_entry.pack(pady=5)

        confirm_button = ttk.Button(
            confirm_window, text="Confirm Delete", command=confirm_deletion
        )
        confirm_button.pack(pady=5)
        exit_button = ttk.Button(
            confirm_window, text="Exit", command=lambda: confirm_window.destroy()
        )
        exit_button.pack(padx=5)

    def update_combobox():
        openai_config_names = [config.name for config in secrets_manager.openai_configs]
        openai_config_combobox["values"] = openai_config_names
        if openai_config_names:
            openai_config_combobox.current(0)
        else:
            openai_config_combobox.set("")  # Clear combobox if no items left

        # Button to update secrets

    def update_secrets():
        # Update Deepgram API key
        new_deepgram_api_key = deepgram_api_key_entry.get()

        # Get the index of the selected OpenAI config
        openai_config_index = openai_config_combobox.current()

        # Call SecretsManager method to update secrets
        secrets_manager.update_secrets(new_deepgram_api_key, openai_config_index)

        # Save settings to file after updating
        secrets_manager.to_json(secrets_manager.settings_filename)

        # Update the combobox to reflect changes
        update_combobox()

        unsaved_changes = True

    def prompt_password():
        password_window = tk.Toplevel(root)
        password_window.title("Authentication Required")
        password_window.geometry("300x150")
        center_window(password_window)
        password_window.resizable(False, False)

        ttk.Label(password_window, text="Enter password:").pack(pady=10)
        password_entry = ttk.Entry(password_window, show="*")
        password_entry.pack(pady=5)

        def check_password():
            if password_entry.get() == "test123":
                password_window.destroy()
                show_admin_panel()
            else:
                messagebox.showerror("Error", "Incorrect password")

        ttk.Button(password_window, text="Submit", command=check_password).pack(pady=10)

    def show_admin_panel():
        # All your admin panel code goes here, as previously defined
        admin_panel = tk.Toplevel(root)
        admin_panel.title("Admin Panel")
        admin_panel.geometry("600x500")
        center_window(admin_panel)
        secrets_manager = SecretsManager()
        config_frame = ttk.Frame(admin_panel, padding="10 10 10 10")
        config_frame.pack(fill="x", expand=True)
        ttk.Label(config_frame, text="Welcome to the Admin Panel").pack(pady=10)

    prompt_password()
