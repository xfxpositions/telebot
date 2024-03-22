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
height = 600

root.geometry(f"{width}x{height}")

# Configure the root to expand the content dynamically
# Grid yapılandırması
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)

center_window(root)

# load settings
settings = Settings()

# VARIABLES
# -------------------------

# General variables
documentation_path = os.path.join("documentation", "documentation.pdf")

# Defining Frames

# Second main frame (right side)
frame2 = tk.Frame(root, width=400, height=600)
frame2.grid(row=0, column=1, sticky="nsew")
frame2.grid_propagate(False)  # Ensures the frame maintains its own size

# Upper frame within the second frame
frame2_upper = tk.Frame(frame2, width=400, height=200)
frame2_upper.pack(expand=False, fill='both', side='top')

# Lower frame within the second frame
frame2_lower = tk.Frame(frame2, width=400, height=400)
frame2_lower.pack(expand=True, fill='both', side='bottom')

# center the window at the start
center_window(root)

# COMPONENTS
# --------------------------

transcription_text = setup_transcription_frame(root, settings)
prompt_message_text, prompt_message_frame = setup_prompt_frame(frame2_lower)
kb_search_text = setup_kbase_frame(frame2_upper, prompt_message_text)
setup_menubar(root, documentation_path)
setup_buttons(root, documentation_path, transcription_text, kb_search_text, prompt_message_text, prompt_message_frame)
center_window(root)

if __name__ == "__main__":
    root.mainloop()
