import tkinter as tk
from tkinter import messagebox
import threading
import traceback
import sys 
from utils.logger import init_logger

def show_error_in_thread(err_message):
    """Function to display the error message in a new thread."""
    def thread_target():
        # Ensure there's a Tk root window instance before showing a message box.
        # This check is crucial for threads that may run before the Tkinter loop starts.
        if not tk._default_root:
            tk.Tk().withdraw() # Hide the root window
        messagebox.showerror("Error Occurred", err_message)

    error_thread = threading.Thread(target=thread_target)
    error_thread.start()

def custom_except_hook(exc_type, exc_value, exc_traceback):
    """Custom exception hook to log errors and show them in a message box."""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    err_message = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    show_error_in_thread(err_message)
    raise Exception (f"Uncaught exception: {err_message}") 
