import sys
import os
import tkinter as tk
from tkinter import messagebox
from utils.general import center_window, open_documentation, exit_app
from ui.settings import open_settings_window


# Menubar
def setup_menubar(root, documentation_path):

    # Define a function to show information about the application
    def show_about():
        # Create a new window for displaying about information
        about_window = tk.Toplevel(root)
        center_window(about_window)
        about_window.geometry("300x300")
        about_window.title("About")
        about_window.resizable(False, False)

        # Display application information
        tk.Label(about_window, text="Logo Telebot", font=("Arial", 16)).pack(
            pady=(10, 0)
        )
        tk.Label(about_window, text="Version: 0.2", font=("Arial", 12)).pack(pady=10)
        tk.Label(
            about_window,
            text="Contributors:\n\nYusuf Karaca\nSinan Yalcinkaya\nBora Bulus",
            font=("Arial", 12),
        ).pack(pady=10)

        # Add a button to view the license
        view_license_btn = tk.Button(
            about_window, text="View License", command=open_license_file
        )
        view_license_btn.pack(pady=(5, 10))

        # Add a button to close the about window
        close_btn = tk.Button(about_window, text="Close", command=about_window.destroy)
        close_btn.pack(pady=5)

    # Opens the license and shows in messagebox
    def open_license_file():
        try:
            with open("LICENSE", "r") as file:
                license_text = file.read()
            messagebox.showinfo("License", license_text)
        except FileNotFoundError:
            messagebox.showerror("Error", "License file not found.")

    # Create a menubar
    menubar = tk.Menu(root)

    # File menu
    menu_file = tk.Menu(menubar, tearoff=0)
    menu_file.add_command(label="Exit", command=lambda: exit_app(root))
    menubar.add_cascade(label="File", menu=menu_file)

    # Settings menu with a submenu
    menu_settings = tk.Menu(menubar, tearoff=0)
    submenu_general_settings = tk.Menu(menu_settings, tearoff=0)
    submenu_general_settings.add_command(label="General", command=open_settings_window)
    menu_settings.add_cascade(label="Settings", menu=submenu_general_settings)
    menubar.add_cascade(label="Settings", menu=menu_settings)

    # Help menu
    menu_help = tk.Menu(menubar, tearoff=0)
    menu_help.add_command(label="About", command=show_about)
    menu_help.add_command(label="Documentation", command=lambda:open_documentation(documentation_path))

    menubar.add_cascade(label="Help", menu=menu_help)

    # Display the menu
    root.config(menu=menubar)
