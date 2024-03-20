import tkinter as tk
from utils.kb import search_kb

def setup_kbase_frame(root, prompt_message_text):
    # KB search frame setup within the upper part of frame2
    kbase_frame = tk.LabelFrame(root, text="Search KB")
    kbase_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    # KB search textbox setup
    kb_search_text = tk.Text(kbase_frame, height=3)
    kb_search_text.insert(tk.END, "Please type your issue here..")
    kb_search_text.pack(fill="both", expand=True, padx=5, pady=5)
    
    # KB search button setup
    search_kb_button = tk.Button(kbase_frame, text="Search in KB", command=lambda: search_kb(prompt_message_text, kb_search_text, search_kb_button))
    search_kb_button.pack(pady=5, padx=5, fill="x")
    
    return kb_search_text