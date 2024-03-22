import tkinter as tk
from tkinter import scrolledtext, messagebox
import os
import pyperclip

from utils.general import center_window  # Ensure pyperclip is installed

def view_log_content(log_text_widget, log_file_path):
    """Open and display the content of a log file in the ScrolledText widget."""
    log_text_widget.delete(1.0, tk.END)  # Clear the current content
    with open(log_file_path, "r") as file:
        log_text_widget.insert(tk.END, file.read())  # Add file content to the widget

def open_logs_window(root, logs_directory="logs"):
    logs_window = tk.Toplevel(root)
    logs_window.title("Debug Logs")
    logs_window.geometry("900x450")
    logs_window.maxsize(1200, 650)
    logs_window.resizable(False, False)
    center_window(logs_window)

    # Use PanedWindow for resizable main content
    main_frame = tk.PanedWindow(logs_window, orient=tk.HORIZONTAL)
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Widget to list log files
    log_listbox = tk.Listbox(main_frame)
    main_frame.add(log_listbox, stretch="always")

    # A new frame to contain the log_text_widget and its horizontal scrollbar
    text_frame = tk.Frame(main_frame)
    main_frame.add(text_frame, stretch="always")

    # Widget to display the content of log files, without adding scrollbar yet
    log_text_widget = scrolledtext.ScrolledText(text_frame, font=('Courier', 10), wrap=tk.NONE)
    log_text_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    # Create and configure a horizontal scrollbar for the log_text_widget
    h_scrollbar = tk.Scrollbar(text_frame, orient=tk.HORIZONTAL, command=log_text_widget.xview)
    log_text_widget.config(xscrollcommand=h_scrollbar.set)
    h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)  # Place the scrollbar directly below the text widget

    # Frame for buttons, adjust to ensure visibility without resizing
    buttons_frame = tk.Frame(logs_window)
    buttons_frame.pack(fill=tk.X, side=tk.BOTTOM)  # Adjusted to fill horizontally

    # Adjust grid layout to align buttons to the right
    buttons_frame.columnconfigure(0, weight=1)  # Add this line to push buttons to the right


    def copy_logs():
        try:
            pyperclip.copy(log_text_widget.get(1.0, tk.END))
            messagebox.showinfo("Success", "Logs copied to clipboard.", parent=logs_window)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy logs: {e}", parent=logs_window)

    def reload_logs():
        log_listbox.delete(0, tk.END)
        log_files = sorted(os.listdir(logs_directory), key=lambda x: os.path.getmtime(os.path.join(logs_directory, x)), reverse=True)
        for log_file in log_files:
            log_listbox.insert(tk.END, log_file)
        if log_files:
            log_listbox.select_set(0)
            view_log_content(log_text_widget, os.path.join(logs_directory, log_files[0]))

    # Buttons with adjusted placement to ensure right alignment
    copy_button = tk.Button(buttons_frame, text="Copy Logs", command=copy_logs)
    copy_button.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

    reload_button = tk.Button(buttons_frame, text="Reload", command=reload_logs)
    reload_button.grid(row=0, column=2, sticky="ew", padx=5, pady=5)

    close_button = tk.Button(buttons_frame, text="Close", command=lambda: logs_window.destroy())
    close_button.grid(row=0, column=3, sticky="ew", padx=5, pady=5)

    def on_log_select(event):
        selection = event.widget.curselection()
        if selection:
            index = selection[0]
            log_file = event.widget.get(index)
            log_file_path = os.path.join(logs_directory, log_file)
            view_log_content(log_text_widget, log_file_path)

    log_listbox.bind('<<ListboxSelect>>', on_log_select)
    reload_logs()  # Initial load of logs