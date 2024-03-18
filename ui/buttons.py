import tkinter as tk
from ui.settings import open_settings_window
from utils.general import open_documentation
from utils.kb import search_kb
from utils.tools import clear_text, copy_text


def setup_buttons(
    root,
    audio,
    documentation_path,
):

    # Buttons frame setup for layout adjustment
    buttons_frame = tk.Frame(root)
    buttons_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
    root.grid_rowconfigure(2, weight=0)  # Keep buttons row from expanding

    right_buttons_frame = tk.Frame(buttons_frame)  # Frame for right-aligned buttons
    right_buttons_frame.pack(side="right")  # Align to the right

    clear_button = tk.Button(buttons_frame, text="Clear", command=clear_text)
    copy_button = tk.Button(buttons_frame, text="Copy", command=copy_text)
    clear_button.pack(side="left", padx=5, pady=5)
    copy_button.pack(side="left", padx=5, pady=5)

    # Right-aligned buttons setup
    help_button = tk.Button(
        right_buttons_frame,
        text="Help",
        command=lambda: open_documentation(documentation_path),
    )
    settings_button = tk.Button(
        right_buttons_frame,
        text="Settings",
        command=lambda: open_settings_window(root),
    )
    exit_button = tk.Button(right_buttons_frame, text="Exit App", command=root.destroy)
    help_button.pack(side="left", padx=5, pady=5)
    settings_button.pack(side="left", padx=5, pady=5)
    exit_button.pack(side="left", padx=5, pady=5)
