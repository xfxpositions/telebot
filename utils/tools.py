import tkinter as tk


# Copies the content of the transcription_text widget to the clipboard.
def copy_text(prompt_message_frame, error_message_text):
    # Get the selected text in prompt message
    selected_text = prompt_message_frame.selection_get()

    # Delete and copy to error message prompt
    error_message_text.delete(1.0, tk.END)
    error_message_text.insert(tk.END, selected_text)


# Clears the content of the transcription_text and error_message_text widgets.
def clear_text(transcription_text, error_message_text, prompt_message_text):
    transcription_text.delete("1.0", tk.END)
    error_message_text.delete("1.0", tk.END)
    prompt_message_text.delete("1.0", tk.END)


# Prints the size of the root window every 500 milliseconds.
def print_size(root):
    print("Window Size: {}x{}".format(root.winfo_width(), root.winfo_height()))
    root.after(
        500, print_size
    )  # Schedule print_size to be called again after 500 milliseconds
