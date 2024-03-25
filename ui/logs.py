import tkinter as tk
from tkinter import scrolledtext, messagebox
import os
import pyperclip

from utils.general import center_window  # Ensure pyperclip is installed

def view_log_content(log_text_widget, log_file_path):
    log_text_widget.delete(1.0, tk.END)
    with open(log_file_path, "r") as file:
        log_text_widget.insert(tk.END, file.read())

def open_logs_window(root, logs_directory="logs"):
    logs_window = tk.Toplevel(root)
    logs_window.title("Debug Logs")
    logs_window.geometry("1000x450")
    logs_window.maxsize(1200, 650)
    logs_window.resizable(False, False)
    center_window(logs_window)

    main_frame = tk.PanedWindow(logs_window, orient=tk.HORIZONTAL)
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Increase width and add a gap using the 'sashpad' parameter of the PanedWindow
    log_listbox = tk.Listbox(main_frame, width=40)  # Increased width
    main_frame.add(log_listbox, stretch="never", padx=10)  # Added padx for gap

    text_frame = tk.Frame(main_frame)
    main_frame.add(text_frame, stretch="always")

    log_text_widget = scrolledtext.ScrolledText(text_frame, font=('Courier', 10), wrap=tk.NONE)
    log_text_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    h_scrollbar = tk.Scrollbar(text_frame, orient=tk.HORIZONTAL, command=log_text_widget.xview)
    log_text_widget.config(xscrollcommand=h_scrollbar.set)
    h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

    buttons_frame = tk.Frame(logs_window)
    buttons_frame.pack(fill=tk.X, side=tk.BOTTOM)
    buttons_frame.columnconfigure(0, weight=1)

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

    def delete_log_entry():
        selection = log_listbox.curselection()
        if selection:
            index = selection[0]
            if index == 0:
                messagebox.showinfo("Action Forbidden", "Cannot delete the first log entry as it's possibly still writing.", parent=logs_window)
                return
            response = messagebox.askyesno("Confirm Deletion", "Do you really want to delete this log file?", parent=logs_window)
            if response:
                log_file = log_listbox.get(index)
                os.remove(os.path.join(logs_directory, log_file))
                reload_logs()

    copy_button = tk.Button(buttons_frame, text="Copy Logs", command=copy_logs)
    copy_button.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

    reload_button = tk.Button(buttons_frame, text="Reload", command=reload_logs)
    reload_button.grid(row=0, column=2, sticky="ew", padx=5, pady=5)

    delete_button = tk.Button(buttons_frame, text="Delete Log Entry", command=delete_log_entry)
    delete_button.grid(row=0, column=3, sticky="ew", padx=5, pady=5)

    close_button = tk.Button(buttons_frame, text="Close", command=lambda: logs_window.destroy())
    close_button.grid(row=0, column=4, sticky="ew", padx=5, pady=5)

    def on_log_select(event):
        selection = event.widget.curselection()
        if selection:
            index = selection[0]
            log_file = event.widget.get(index)
            log_file_path = os.path.join(logs_directory, log_file)
            view_log_content(log_text_widget, log_file_path)

    log_listbox.bind('<<ListboxSelect>>', on_log_select)
    reload_logs()  # Initial load of logs
