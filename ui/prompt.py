import tkinter as tk



def setup_prompt_frame(frame2_lower):
    # Admin message frame setup within the lower part of frame2
    prompt_message_frame = tk.LabelFrame(frame2_lower, text="Prompt")
    prompt_message_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Admin message textbox setup
    prompt_message_text = tk.Text(prompt_message_frame, height=4)
    prompt_message_text.insert(tk.END, "Please make a kbase call..")
    prompt_message_text.pack(fill="both", expand=True, padx=5, pady=5)
    
    return prompt_message_text, prompt_message_frame