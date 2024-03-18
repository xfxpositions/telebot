import tkinter as tk


def setup_prompt_frame(root):
    # Admin message frame setup
    prompt_message_frame = tk.LabelFrame(root, text="Prompt")
    prompt_message_frame.grid(
        row=1, column=0, columnspan=2, padx=10, pady=0, sticky="nsew"
    )

    # Admin message textbox setup
    prompt_message_text = tk.Text(prompt_message_frame, height=4, width=88)
    prompt_message_text.insert(
        tk.END,
        "Sorununuz şu şundan kaynaklanmaktadır. Şöyle ve şöyle yaparak çözebilirsiniz.",
    )
    prompt_message_text.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
    prompt_message_frame.grid_rowconfigure(0, weight=1)
    prompt_message_frame.grid_columnconfigure(0, weight=1)
