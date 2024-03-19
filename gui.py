import tkinter as tk
from ui.buttons import setup_buttons
from ui.kbase import setup_kbase_frame
from ui.prompt import setup_prompt_frame
from ui.transcription import setup_transcription_frame
from utils.general import (
    load_settings,
    center_window,
)
import os
import pyaudio
from ui.menubar import setup_menubar
from ui.settings import *
from utils.settings import Settings

# CONFIG
# -------------------------

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
settings = Settings()

# VARIABLES
# -------------------------

# General variables
documentation_path = os.path.join("documentation", "documentation.pdf")


# COMPONENTS
# --------------------------

prompt_message_text = setup_prompt_frame(root)
transcription_text = setup_transcription_frame(root, settings)
error_message_text = setup_kbase_frame(root, prompt_message_text)
setup_buttons(root, documentation_path=documentation_path)
setup_menubar(root, documentation_path)
center_window(root)

if __name__ == "__main__":
    root.mainloop()
