import tkinter as tk
from utils.kbase import make_openai_request_with_question, make_openai_request
import threading
from utils.settings import Settings
from utils.secretsmanager import SecretsManager

openai_config_file_path = "openai_config.json"


# Searches for the provided text in the knowledge base.
def search_kb(
    prompt_message_text: tk.Text,
    error_message_text: tk.Text,
    search_kb_button: tk.Button,
):
    # Clear the past prompt
    prompt_message_text.delete("1.0", tk.END)

    textbox = prompt_message_text

    # Get the text from textbox
    text = error_message_text.get("1.0", "end-1c")

    # Set search button text to sending
    button_old_text = search_kb_button.cget("text")
    search_kb_button.config(text="Sending...")

    def background_task():
        settings = Settings()

        print(settings.openai_index)
        response = make_openai_request(question=text, index_name=settings.openai_index)
        prompt = ""
        if response["error"] == True:
            prompt = response["err"]
        else:
            prompt = response["prompt"]

        # Update gui safely
        def update_gui():
            textbox.delete("1.0", "end")  # Clear previous text
            textbox.insert("1.0", prompt)
            search_kb_button.config(text=button_old_text)

        # Update gui in the main thread
        textbox.after(0, update_gui)

    # Run background thread
    thread = threading.Thread(target=background_task)
    thread.start()
