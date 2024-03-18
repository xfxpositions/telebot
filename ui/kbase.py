import tkinter as tk
from utils.kb import search_kb


def setup_kbase_frame(root):

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

    search_kb_button = tk.Button(
        error_message_frame,
        text="Search in KB",
        command=lambda: search_kb(
            prompt_message_text,
            error_message_text,
        ),
    )
    search_kb_button.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
