import tkinter as tk
from ui.transcription import start_transcription
from utils.kb import search_kb

# Initializes transcription and starts audio stream
from utils.transcription import start_audio_server, init_live_transcription, init_deepgram
import tkinter as tk
from threading import Event
from utils.settings import Settings
from ui.menubar import setup_menubar
from ui.buttons import setup_buttons
from utils.settings import Settings

# Initialize the toggle event and transcription toggle function at a global scope
toggle_event = Event()
toggle_transcription = None

transcription_running = False
first_run = True

# Initialize deepgram client
deepgram = init_deepgram()

settings = Settings()

def setup_transcription_frame(root, settings):
    # Transcription frame setup
    transcription_frame = tk.LabelFrame(root, text="Transcription:")
    transcription_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    # Conversation textbox setup
    transcription_text = tk.Text(transcription_frame)
    transcription_text.insert(
        tk.END,
        "Merhabalar, ben Mahmut Yazılımdan arıyorum.\nBilgisayarımda Logo ERP vardı fakat bugün giriş yapamıyorum. Bana yardımcı olur musunuz?",
    )
    transcription_text.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
    transcription_frame.grid_rowconfigure(0, weight=1)
    transcription_frame.grid_columnconfigure(0, weight=1)

    # Scrollbar for the transcription text
    scrollbar = tk.Scrollbar(transcription_frame, orient="vertical", command=transcription_text.yview)
    scrollbar.grid(row=0, column=1, sticky="ns")
    transcription_text.config(yscrollcommand=scrollbar.set)

    # Position buttons appropriately
    start_stop_button = tk.Button(
        transcription_frame, text="Start Transcription", command=lambda: start_transcription(transcription_text, start_stop_button, settings)
    )
    start_stop_button.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

    return transcription_text

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

def setup_prompt_frame(frame2_lower):
    # Admin message frame setup within the lower part of frame2
    prompt_message_frame = tk.LabelFrame(frame2_lower, text="Prompt")
    prompt_message_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Admin message textbox setup
    prompt_message_text = tk.Text(prompt_message_frame, height=4)
    prompt_message_text.insert(tk.END, "Sorununuz şu şundan kaynaklanmaktadır. Şöyle ve şöyle yaparak çözebilirsiniz.")
    prompt_message_text.pack(fill="both", expand=True, padx=5, pady=5)
    
    return prompt_message_text


# Ana pencereyi oluştur
root = tk.Tk()
root.title("Tkinter Uygulaması")

# Pencere boyutunu ayarla
root.geometry("800x600")

# İlk ana frame (sol taraf)
transcription_text = setup_transcription_frame(root, settings)

# İkinci ana frame (sağ taraf)
frame2 = tk.Frame(root, width=400, height=600, bg="blue")
frame2.grid(row=0, column=1, sticky="nsew")
frame2.grid_propagate(False) # Frame'in kendi boyutunu korumasını sağlar

# İkinci frame içindeki üst frame
frame2_upper = tk.Frame(frame2, width=400, height=200)
frame2_upper.pack(expand=False, fill='both', side='top')

# İkinci frame içindeki alt frame
frame2_lower = tk.Frame(frame2, width=400, height=400)
frame2_lower.pack(expand=True, fill='both', side='bottom')


# Grid yapılandırması
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)

prompt_message_text = setup_prompt_frame(frame2_lower)
kb_search_text = setup_kbase_frame(frame2_upper, prompt_message_text)


setup_menubar(root, None)
setup_buttons(root, None)
root.mainloop()
