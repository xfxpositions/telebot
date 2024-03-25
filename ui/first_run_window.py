import tkinter as tk
from tkinter import messagebox, scrolledtext
import pyperclip
from utils.settings import Settings
from utils.general import open_documentation, center_window

class FirstRunWindow:
    def __init__(self, root: tk.Tk):
        self.toproot = root
        self.root = tk.Toplevel(root)
        self.settings = Settings()
        self.root.title("First Run Setup")
        self.root.geometry("450x400")
        self.root.resizable(False, False)
        center_window(self.root)
        self.setup_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def setup_ui(self):
        self.step_frames = [tk.Frame(self.root) for _ in range(3)]
        for i, frame in enumerate(self.step_frames):
            frame.grid(row=0, column=0, sticky='nsew', padx=20, pady=20)
            self.root.grid_rowconfigure(0, weight=1)
            self.root.grid_columnconfigure(0, weight=1)

        self.welcome_message()
        self.env_entry()
        self.openai_config_entry()
        self.step_frames[0].tkraise()

    def welcome_message(self):
        label = tk.Label(self.step_frames[0], text="Welcome to the First Run Setup", font=("Arial", 14))
        label.pack(pady=20)
        label = tk.Label(self.step_frames[0], text="This wizard will help you for completing the setup Telebot", font=("Arial", 11))
        label.pack(pady=20)

        next_button = tk.Button(self.step_frames[0], text="Next", width=20, command=lambda: self.show_next_step(1))
        next_button.pack(pady=10)

    def env_entry(self):
        label = tk.Label(self.step_frames[1], text="Enter your .env configuration:", font=("Arial", 12))
        label.pack(pady=10)
        self.env_text = scrolledtext.ScrolledText(self.step_frames[1], height=5)
        self.env_text.pack(expand=True, fill='both', pady=10)
        self.add_clear_paste_buttons(self.env_text, self.step_frames[1])
        next_button = tk.Button(self.step_frames[1], text="Next", width=20, command=lambda: self.save_and_proceed(self.env_text.get("1.0", tk.END), ".env", 2))
        next_button.pack(pady=10)

    def openai_config_entry(self):
        label = tk.Label(self.step_frames[2], text="Enter your OpenAI configuration:", font=("Arial", 12))
        label.pack(pady=10)
        self.openai_text = scrolledtext.ScrolledText(self.step_frames[2], height=15)
        self.openai_text.pack(expand=True, fill='both', pady=10)
        self.add_clear_paste_buttons(self.openai_text, self.step_frames[2])
        finish_button = tk.Button(self.step_frames[2], text="Finish", width=20, command=lambda: self.save_and_finish(self.openai_text.get("1.0", tk.END), "openai_config.json"))
        finish_button.pack(pady=10)

    def add_clear_paste_buttons(self, text_widget, frame):
        clear_button = tk.Button(frame, text="Clear", command=lambda: text_widget.delete('1.0', tk.END))
        clear_button.pack(side=tk.LEFT, padx=(0, 10))
        paste_button = tk.Button(frame, text="Paste", command=lambda: text_widget.insert(tk.END, pyperclip.paste()))
        paste_button.pack(side=tk.RIGHT, padx=(10, 0))

    def show_next_step(self, step_index):
        if step_index < len(self.step_frames):
            self.step_frames[step_index].tkraise()

    def save_and_proceed(self, text, filename, next_step):
        if text.strip():
            with open(filename, 'w') as file:
                file.write(text.strip())
            self.show_next_step(next_step)
        else:
            messagebox.showwarning("Warning", "Please enter the required information before proceeding.")

    def save_and_finish(self, text, filename):
        if text.strip():
            with open(filename, 'w') as file:
                file.write(text.strip())
            if messagebox.askyesno("Setup Complete", "You're all set. Do you want to see the documentation?"):
                print("Opening documentation...")
                open_documentation(path=self.settings.documentation_path)
            # Set first run to False for not opening it again
            self.settings.first_run = False
            self.settings.save_settings()
            self.root.destroy()
        else:
            messagebox.showwarning("Warning", "Please enter the required information before proceeding.", parent=self.root)
    def on_close(self):
        # Bring the toproot window to the front
        self.toproot.deiconify()
        self.toproot.focus_set()
        # Then immediately bring the FirstRunWindow back to front
        self.root.deiconify()
        self.root.focus_set()
        self.root.attributes('-topmost', 1)
        self.root.after(100, lambda: self.root.attributes('-topmost', 0))
