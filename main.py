import os
import time
import threading
import tkinter as tk
from tkinter import ttk
import pyttsx3
import pygame

pygame.mixer.init()

APP_TITLE = "Radio Trainer"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PHONETIC_PATH = os.path.join(BASE_DIR, "audio", "phonetic")
MORSE_PATH = os.path.join(BASE_DIR, "audio", "morse")

MORSE_CODE = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..',
    'E': '.', 'F': '..-.', 'G': '--.', 'H': '....',
    'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..',
    'M': '--', 'N': '-.', 'O': '---', 'P': '.--.',
    'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-',
    'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
    'Y': '-.--', 'Z': '--..',
    '0': '-----', '1': '.----', '2': '..---', '3': '...--',
    '4': '....-', '5': '.....', '6': '-....', '7': '--...',
    '8': '---..', '9': '----.'
}

PHONETIC_MAP = {
    'A': 'ALPHA', 'B': 'BRAVO', 'C': 'CHARLIE', 'D': 'DELTA',
    'E': 'ECHO', 'F': 'FOXTROT', 'G': 'GOLF', 'H': 'HOTEL',
    'I': 'INDIA', 'J': 'JULIET', 'K': 'KILO', 'L': 'LIMA',
    'M': 'MIKE', 'N': 'NOVEMBER', 'O': 'OSCAR', 'P': 'PAPA',
    'Q': 'QUEBEC', 'R': 'ROMEO', 'S': 'SIERRA', 'T': 'TANGO',
    'U': 'UNIFORM', 'V': 'VICTOR', 'W': 'WHISKEY', 'X': 'XRAY',
    'Y': 'YANKEE', 'Z': 'ZULU',
    '0': 'ZERO', '1': 'ONE', '2': 'TWO', '3': 'THREE',
    '4': 'FOUR', '5': 'FIVE', '6': 'SIX', '7': 'SEVEN',
    '8': 'EIGHT', '9': 'NINE'
}


class Player(threading.Thread):
    def __init__(self, text, mode, update_status,
                 phonetic_spacing=0.2,
                 morse_symbol_spacing=0.15,
                 morse_letter_spacing=0.3,
                 morse_word_spacing=0.7,
                 phonetic_word_spacing=0.5,
                 tts_word_spacing=0.5):
        super().__init__()
        self.text = text.strip()
        self.mode = mode
        self.update_status = update_status
        self._stop_event = threading.Event()

        self.phonetic_spacing = phonetic_spacing
        self.morse_symbol_spacing = morse_symbol_spacing
        self.morse_letter_spacing = morse_letter_spacing
        self.morse_word_spacing = morse_word_spacing
        self.phonetic_word_spacing = phonetic_word_spacing
        self.tts_word_spacing = tts_word_spacing

    def stop(self):
        self._stop_event.set()
        pygame.mixer.music.stop()

    def run(self):
        if not self.text:
            self.update_status("⚠️ No text to play.")
            return
        try:
            if self.mode == "phonetic":
                self.speak_phonetic()
            elif self.mode == "morse":
                self.speak_morse()
            elif self.mode == "normal":
                self.speak_normal()
            else:
                self.update_status(f"❌ Unknown mode: {self.mode}")
        except Exception as e:
            self.update_status(f"Error: {e}")

    def _play_sound(self, path):
        if not os.path.exists(path):
            self.update_status(f"Missing audio file: {os.path.basename(path)}")
            return
        pygame.mixer.music.load(path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            if self._stop_event.is_set():
                pygame.mixer.music.stop()
                break
            time.sleep(0.01)

    def speak_phonetic(self):
        self.update_status("Phonetic Mode")
        for char in self.text.upper():
            if self._stop_event.is_set():
                break
            if char.isalnum():
                word = PHONETIC_MAP.get(char, char)
                self.update_status(f"{char} → {word}")
                path = os.path.join(PHONETIC_PATH, f"{char.lower()}.mp3")
                self._play_sound(path)
                time.sleep(self.phonetic_spacing)
            elif char == " ":
                self.update_status("Space")
                time.sleep(self.phonetic_word_spacing)
        self.update_status("Done.")

    def speak_morse(self):
        self.update_status("•– Morse Mode")
        dot = os.path.join(MORSE_PATH, "dot.wav")
        dash = os.path.join(MORSE_PATH, "dash.wav")

        for char in self.text.upper():
            if self._stop_event.is_set():
                break
            if char == " ":
                self.update_status("Space")
                time.sleep(self.morse_word_spacing)
                continue
            code = MORSE_CODE.get(char)
            if not code:
                continue
            self.update_status(f"{char} → {code}")
            for symbol in code:
                if self._stop_event.is_set():
                    break
                self.update_status(f"{char} → {symbol}")
                if symbol == '.':
                    self._play_sound(dot)
                else:
                    self._play_sound(dash)
                time.sleep(self.morse_symbol_spacing)
            time.sleep(self.morse_letter_spacing)
        self.update_status("✅ Done.")

    def speak_normal(self):
        self.update_status("🗣️ Normal Speech Mode")
        engine = pyttsx3.init()
        engine.setProperty('rate', 175)
        # Pick voice (Windows example)
        for voice in engine.getProperty('voices'):
            if "Zira" in voice.name or "David" in voice.name:
                engine.setProperty('voice', voice.id)
                break
        self.update_status(f"Speaking full text")
        engine.say(self.text)
        engine.runAndWait()
        time.sleep(self.tts_word_spacing)
        engine.stop()
        self.update_status("Done.")


class RadioTrainerApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("540x560")
        self.root.minsize(400, 400)
        self.root.resizable(True, True)  # Allow resizing

        # No special theme — default Tkinter style
        self.mode = tk.StringVar(value="phonetic")
        self.player = None

        self.phonetic_spacing = tk.DoubleVar(value=0.2)
        self.phonetic_word_spacing = tk.DoubleVar(value=0.5)
        self.morse_symbol_spacing = tk.DoubleVar(value=0.15)
        self.morse_letter_spacing = tk.DoubleVar(value=0.3)
        self.morse_word_spacing = tk.DoubleVar(value=0.7)
        self.tts_word_spacing = tk.DoubleVar(value=0.5)

        self._build_ui()
        self.update_spacing_controls()  # show/hide spacing sliders per mode

    def _build_ui(self):
        ttk.Label(self.root, text=APP_TITLE, font=("Segoe UI", 20, "bold")).pack(pady=10)

        self.text_widget = tk.Text(self.root, wrap="word", height=6, font=("Consolas", 14))
        self.text_widget.insert("1.0", "CQ CQ de VK3??? testing")
        self.text_widget.pack(padx=20, pady=10, fill="both", expand=True)

        mode_frame = ttk.LabelFrame(self.root, text="Mode")
        mode_frame.pack(padx=20, pady=10, fill="x")

        for text, value in [
            ("Phonetic Alphabet", "phonetic"),
            ("Morse Code", "morse"),
            ("Normal Speech (TTS)", "normal")
        ]:
            ttk.Radiobutton(mode_frame, text=text, variable=self.mode, value=value,
                            command=self.update_spacing_controls).pack(anchor="w", padx=12, pady=3)

        # Spacing sliders frame
        self.spacing_frame = ttk.LabelFrame(self.root, text="Spacing Settings (seconds)")
        self.spacing_frame.pack(padx=20, pady=10, fill="x")

        # Phonetic spacing sliders
        self.phonetic_spacing_label = ttk.Label(self.spacing_frame, text="Between Characters:")
        self.phonetic_spacing_slider = ttk.Scale(self.spacing_frame, from_=0.0, to=1.0,
                                                 variable=self.phonetic_spacing, orient="horizontal")
        self.phonetic_word_spacing_label = ttk.Label(self.spacing_frame, text="Between Words:")
        self.phonetic_word_spacing_slider = ttk.Scale(self.spacing_frame, from_=0.0, to=2.0,
                                                      variable=self.phonetic_word_spacing, orient="horizontal")

        # Morse spacing sliders
        self.morse_symbol_spacing_label = ttk.Label(self.spacing_frame, text="Between Symbols:")
        self.morse_symbol_spacing_slider = ttk.Scale(self.spacing_frame, from_=0.0, to=1.0,
                                                     variable=self.morse_symbol_spacing, orient="horizontal")
        self.morse_letter_spacing_label = ttk.Label(self.spacing_frame, text="Between Letters:")
        self.morse_letter_spacing_slider = ttk.Scale(self.spacing_frame, from_=0.0, to=2.0,
                                                     variable=self.morse_letter_spacing, orient="horizontal")
        self.morse_word_spacing_label = ttk.Label(self.spacing_frame, text="Between Words:")
        self.morse_word_spacing_slider = ttk.Scale(self.spacing_frame, from_=0.0, to=3.0,
                                                   variable=self.morse_word_spacing, orient="horizontal")

        # TTS spacing slider
        self.tts_word_spacing_label = ttk.Label(self.spacing_frame, text="Pause After Speech (seconds):")
        self.tts_word_spacing_slider = ttk.Scale(self.spacing_frame, from_=0.0, to=2.0,
                                                 variable=self.tts_word_spacing, orient="horizontal")

        # Buttons frame
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="▶ Play", command=self.on_play).pack(side="left", padx=15)
        ttk.Button(button_frame, text="⏹ Stop", command=self.on_stop).pack(side="left", padx=15)

        # Status label
        self.status_label = ttk.Label(self.root, text="Ready.", font=("Segoe UI", 10))
        self.status_label.pack(side="bottom", pady=10)

    def update_spacing_controls(self):
        # Clear spacing frame
        for widget in self.spacing_frame.winfo_children():
            widget.pack_forget()

        mode = self.mode.get()

        if mode == "phonetic":
            self.phonetic_spacing_label.pack(anchor="w", padx=10, pady=(5, 0))
            self.phonetic_spacing_slider.pack(fill="x", padx=10)
            self.phonetic_word_spacing_label.pack(anchor="w", padx=10, pady=(10, 0))
            self.phonetic_word_spacing_slider.pack(fill="x", padx=10)

        elif mode == "morse":
            self.morse_symbol_spacing_label.pack(anchor="w", padx=10, pady=(5, 0))
            self.morse_symbol_spacing_slider.pack(fill="x", padx=10)
            self.morse_letter_spacing_label.pack(anchor="w", padx=10, pady=(10, 0))
            self.morse_letter_spacing_slider.pack(fill="x", padx=10)
            self.morse_word_spacing_label.pack(anchor="w", padx=10, pady=(10, 0))
            self.morse_word_spacing_slider.pack(fill="x", padx=10)

        elif mode == "normal":
            self.tts_word_spacing_label.pack(anchor="w", padx=10, pady=(5, 0))
            self.tts_word_spacing_slider.pack(fill="x", padx=10)

    def on_play(self):
        if self.player and self.player.is_alive():
            self.update_status("❗ Already playing.")
            return
        text = self.text_widget.get("1.0", "end").strip()
        if not text:
            self.update_status("⚠️ Please enter some text.")
            return
        self.player = Player(
            text=text,
            mode=self.mode.get(),
            update_status=self.update_status,
            phonetic_spacing=self.phonetic_spacing.get(),
            phonetic_word_spacing=self.phonetic_word_spacing.get(),
            morse_symbol_spacing=self.morse_symbol_spacing.get(),
            morse_letter_spacing=self.morse_letter_spacing.get(),
            morse_word_spacing=self.morse_word_spacing.get(),
            tts_word_spacing=self.tts_word_spacing.get()
        )
        self.player.start()

    def on_stop(self):
        if self.player and self.player.is_alive():
            self.player.stop()
            self.update_status("⏹ Stopped.")
        else:
            self.update_status("Nothing to stop.")

    def update_status(self, text):
        def inner():
            self.status_label.config(text=text)
        self.root.after(0, inner)


if __name__ == "__main__":
    root = tk.Tk()
    app = RadioTrainerApp(root)
    root.mainloop()
