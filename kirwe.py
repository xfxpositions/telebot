import tkinter as tk

# Create the main window
root = tk.Tk()
root.title("Telebot")

# Create frames
transcription_frame = tk.Frame(root)
search_frame = tk.Frame(root)
prompt_frame = tk.Frame(root)

# Layout frames
transcription_frame.grid(row=0, column=0, sticky="nsew")
search_frame.grid(row=0, column=1, sticky="nsew")
prompt_frame.grid(row=1, column=1, sticky="nsew")

# Configure rows and columns weights
root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=2)
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)

# Add widgets to transcription frame
transcription_text = tk.Text(transcription_frame)
transcription_text.pack(expand=True, fill="both")

# Add widgets to search frame
search_text = tk.Text(search_frame, height=3)
search_text.pack(expand=True, fill="x")
search_button = tk.Button(search_frame, text="Search in KB")
search_button.pack(fill="x")

# Add widgets to prompt frame
prompt_text = tk.Text(prompt_frame)
prompt_text.pack(expand=True, fill="both")

# Add bottom buttons
bottom_frame = tk.Frame(root)
bottom_frame.grid(row=2, column=0, columnspan=2, sticky="ew")
start_stop_button = tk.Button(bottom_frame, text="Start/Stop")
clear_button = tk.Button(bottom_frame, text="Clear")
copy_button = tk.Button(bottom_frame, text="Copy")
help_button = tk.Button(bottom_frame, text="HELP")
settings_button = tk.Button(bottom_frame, text="Settings")
exit_button = tk.Button(bottom_frame, text="Exit App")
# Layout the buttons in the bottom_frame using .pack() or .grid()

# Run the application
root.mainloop()
