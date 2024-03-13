import customtkinter as ctk
import pyaudio
import tkinter as tk
import numpy as np
from tkinter import messagebox
from azure.cognitiveservices.speech import SpeechConfig, SpeechRecognizer, AudioConfig, ResultReason, CancellationReason
import threading
from utils import center_tkinter_window, list_audio_devices, init_deepgram, init_stream_audio, init_live_transcription
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.deepgram = init_deepgram()
        self.stream_url = None
        
        self.title('Ses Çıkış Ayarları')
        self.geometry('800x550')
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.is_streaming = False
        
        # List available audio devices
        self.device_list = list_audio_devices(self.audio)
        self.selected_device = tk.StringVar(self)
        self.selected_device_index = 1

        # Center at start 
        self.center_mainframe()


        # Create a top menu
        self.create_menu()

        # Create a main frame
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(pady=20, padx=20, fill='both', expand=True)

        # Create frames for Transcription and Search
        self.transcription_menu = ctk.CTkFrame(self.main_frame)
        self.transcription_menu.grid(row=1, column=0, pady=20, padx=20, sticky="nsew")

        self.search_menu = ctk.CTkFrame(self.main_frame)
        self.search_menu.grid(row=1, column=1, pady=20, padx=20, sticky="nsew")

        # Configure the grid
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)

        # Transcription components
        self.transcription_label = ctk.CTkLabel(self.transcription_menu, text="Transcription:")
        self.transcription_label.pack(pady=20)

        # Start/Stop button
        self.toggle_button = ctk.CTkButton(self.transcription_menu, text='Başlat',
                                           command=self.toggle_stream)
        self.toggle_button.pack(pady=10)


        self.transcription_textbox = ctk.CTkTextbox(self.transcription_menu, height=200, width=280, corner_radius=10)
        self.transcription_textbox.pack(pady=60)


        # Search components
        self.search_label = ctk.CTkLabel(self.search_menu, text="Search:")
        self.search_label.pack(pady=20)

        self.search_entry = ctk.CTkEntry(self.search_menu, width=200, corner_radius=10)
        self.search_entry.pack(pady=10)

        self.search_button = ctk.CTkButton(self.search_menu, text="Search",
                                           command=self.search_function)  # Placeholder for actual search function
        self.search_button.pack(pady=10)
        
        self.search_textbox = ctk.CTkTextbox(self.search_menu, height=200, width=280, corner_radius=10)
        self.search_textbox.pack(pady=20)

    def center_window(self):
        window_width = self.winfo_reqwidth()
        window_height = self.winfo_reqheight()
        position_right = int(self.winfo_screenwidth()/2 - window_width/2)
        position_down = int(self.winfo_screenheight()/2 - window_height/2)
        self.geometry(f"+{position_right}+{position_down}")

    def create_menu(self):
        # Create a top menu
        menubar = tk.Menu(self)
        self.configure(menu=menubar)

        # Add a "Settings" option
        settings_menu = tk.Menu(menubar, tearoff=0)
        settings_menu.add_command(label="Audio Settings", command=self.show_audio_settings)
        menubar.add_cascade(label="Settings", menu=settings_menu)

        # Add an "About" option
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about_info)
        menubar.add_cascade(label="Help", menu=help_menu)

    def show_about_info(self):
        # Display about information
        messagebox.showinfo("About", "This application is a simple audio streaming control tool.")

    def toggle_stream(self):
        if not self.is_streaming:
            self.start_stream()
            self.is_streaming = True
            self.toggle_button.configure(text='Dur')  # Change status from "Start" to "Stop"
            # Start speech recognition in a new thread
            self.start_speech_recognition()
        else:
            self.stop_stream()
            self.is_streaming = False
            self.toggle_button.configure(text='Başlat')  # Change status from "Stop" to "Start"

    def start_stream(self):
        device_index = self.device_list.index(self.selected_device.get())
        self.stream = self.audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True,
                                      frames_per_buffer=CHUNK, input_device_index=device_index)
        self.stream.start_stream()
        self.start_speech_recognition()
        
    def center_mainframe(self):
        width = 800 # Width 
        height = 550 # Height
        
        screen_width = self.winfo_screenwidth()  # Width of the screen
        screen_height = self.winfo_screenheight() # Height of the screen
        
        # Calculate Starting X and Y coordinates for Window
        x = (screen_width/2) - (width/2)
        y = (screen_height/2) - (height/2)
        
        self.geometry('%dx%d+%d+%d' % (width, height, x, y))

    def start_speech_recognition(self):
        if self.is_streaming:
            # Start audio streaming
            self.stream_url = init_stream_audio(self.port, self.selected_device_index)
            
            # Start the speech recognition in a new thread
            recognition_thread = threading.Thread(target=self.recognize, daemon=True)
            recognition_thread.start()

    def recognize(self):
        while self.is_streaming:
            result = self.speech_recognizer.recognize_once()
            if result.reason == ResultReason.RecognizedSpeech:
                print(f"Recognized: {result.text}")
                self.transcription_textbox.insert(tk.END, f"{result.text}\n")
            elif result.reason == ResultReason.NoMatch:
                print("No speech recognized.")
            elif result.reason == ResultReason.Canceled:
                cancellation_details = result.cancellation_details
                print(f"Cancellation reason: {cancellation_details.reason}")
                if cancellation_details.reason == CancellationReason.Error:
                    print(f"Error: {cancellation_details.error_details}")

    def stop_stream(self):
        if self.stream:
            self.is_streaming = False  # Stop the speech recognition loop
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
            if self.speech_recognizer:
                self.speech_recognizer.stop_continuous_recognition()
                self.speech_recognizer = None

    def search_function(self):
        # Placeholder for actual search function
        # Implement search functionality based on search_entry contents
        pass

    @staticmethod
    def stream_callback(in_data, frame_count, time_info, status):
        audio_data = np.frombuffer(in_data, dtype=np.int16)
        volume = np.linalg.norm(audio_data) * 10
        print(f"Volume: {volume}, Frame Count: {frame_count}, Status: {status}")
        return in_data, pyaudio.paContinue

    def show_audio_settings(self):
        # Create a new top-level window for the settings
        settings_window = ctk.CTkToplevel(self)
        settings_window.title("Audio Settings")
        
        settings_window.geometry("480x240")

        # Label for device selection within the settings window
        device_label = ctk.CTkLabel(settings_window, text="Giriş cihazını seçiniz", font=ctk.CTkFont(size=18))
        device_label.pack(pady=10)

        # Dropdown for device selection within the settings window
        dropdown = ctk.CTkOptionMenu(settings_window, variable=self.selected_device,
                                     values=self.device_list, width=340, dynamic_resizing=False, corner_radius=10)

        self.selected_device.trace_variable("w", self.on_device_change)
        
        dropdown.pack(pady=20)
    def on_device_change(self, *args):
        selected_value = self.selected_device.get()

        self.selected_device_index = self.device_list.index(self.selected_device.get())

        print("Selected Device:", selected_value)
        print("Selected Device index:", self.selected_device_index)


if __name__ == '__main__':
    app = App()
    app.mainloop()
 