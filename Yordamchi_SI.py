import tkinter as tk
from tkinter import filedialog, Menu, Frame
from PIL import Image, ImageTk, ImageOps
import pytesseract
import cv2
import pyttsx3
import threading
import os
import json
from ultralytics import YOLO
import sounddevice as sd
import vosk

yolo_model = YOLO("yolov8n.pt")
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

engine = pyttsx3.init()
engine.setProperty('rate', 170)
engine.setProperty('volume', 0.9)

def speak_async(text):
    def _worker(t):
        try:
            engine.say(t)
            engine.runAndWait()
        except:
            pass
    threading.Thread(target=_worker, args=(text,), daemon=True).start()

translations = {
    "person": "odam", "car": "mashina", "cat": "mushuk", "dog": "it",
    "chair": "stul", "cup": "chashka", "laptop": "noutbuk", "phone": "telefon",
    "bottle": "shisha", "book": "kitob", "keyboard": "klaviatura",
    "bus": "avtobus", "truck": "yuk mashinasi", "bird": "qush",
    "tv": "televizor", "table": "stol", "knife": "pichoq"
}

def set_tts_voice_for_lang(lang_code):
    try:
        voices = engine.getProperty('voices')
        for v in voices:
            vmeta = f"{v.id} {v.name} {v.languages}".lower()
            if lang_code == "uz" and ("uz" in vmeta or "uzbek" in vmeta):
                engine.setProperty('voice', v.id)
                return
            if lang_code == "ru" and ("ru" in vmeta or "russian" in vmeta):
                engine.setProperty('voice', v.id)
                return
            if lang_code == "en" and ("en" in vmeta or "english" in vmeta):
                engine.setProperty('voice', v.id)
                return
    except:
        pass

VOSK_MODELS = {
    "en": "models/vosk-model-small-en-us-0.15",
    "ru": "models/vosk-model-small-ru-0.22",
    "uz": "models/vosk-model-small-uz-0.1"
}

class AIAssistantApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Yordamchi SI Kurs ishim uchun (Sultonov Sardorbek Qudrat o'g'li) ")
        self.root.geometry("1200x780")
        self.root.configure(bg="#f9f9f9")

        self.cap = None
        self.stop_camera = True
        self.last_detected = ""
        self.current_lang = "uz"
        set_tts_voice_for_lang(self.current_lang)

        self.ui_texts = {
            "title": {"uz": "Asosiy menyu", "ru": "Главное меню", "en": "Main Menu"},
            "start_cam": {"uz": "Kamerani ishga tushurish", "ru": "Запустить камеру", "en": "Start Camera"},
            "stop_cam": {"uz": "Kamerani to‘xtatish", "ru": "Остановить камеру", "en": "Stop Camera"},
            "open_img": {"uz": "Rasm yuklash va o‘qish", "ru": "Открыть изображение", "en": "Open Image"},
            "stt": {"uz": "Ovozdan matnga", "ru": "Речь в текст", "en": "Speech to Text"},
            "tts": {"uz": "Matndan ovozga", "ru": "Текст в речь", "en": "Text to Speech"}
        }

        menubar = Menu(root)
        lang_menu = Menu(menubar, tearoff=0)
        lang_menu.add_command(label="O‘zbek", command=lambda: self.change_language("uz"))
        lang_menu.add_command(label="Русский", command=lambda: self.change_language("ru"))
        lang_menu.add_command(label="English", command=lambda: self.change_language("en"))
        menubar.add_cascade(label="Til", menu=lang_menu)
        root.config(menu=menubar)

        self.left_frame = tk.Frame(root, bg="#eef")
        self.left_frame.pack(side="left", fill="y", padx=18, pady=18)

        tk.Label(self.left_frame, text=self.ui_texts["title"][self.current_lang],
                 font=("Segoe UI", 16, "bold"), bg="#eef").pack(pady=20)

        tk.Button(self.left_frame, text=self.ui_texts["start_cam"][self.current_lang],
                  font=("Segoe UI", 12), bg="#d1c4e9", width=34, command=self.start_camera).pack(pady=8)

        tk.Button(self.left_frame, text=self.ui_texts["stop_cam"][self.current_lang],
                  font=("Segoe UI", 12), bg="#ffcdd2", width=34, command=self.stop_camera_func).pack(pady=8)

        tk.Button(self.left_frame, text=self.ui_texts["open_img"][self.current_lang],
                  font=("Segoe UI", 12), bg="#d1e7dd", width=34, command=self.open_image).pack(pady=8)

        tk.Button(self.left_frame, text=self.ui_texts["stt"][self.current_lang],
                  font=("Segoe UI", 12), bg="#cff4fc", width=34, command=self.speech_to_text).pack(pady=8)

        self.right_frame = tk.Frame(root, bg="#fff")
        self.right_frame.pack(side="right", expand=True, fill="both", padx=18, pady=18)

        self.canvas = tk.Canvas(self.right_frame, bg="#000", width=700, height=420)
        self.canvas.pack(pady=10)

        self.output_label = tk.Label(self.right_frame, text="", font=("Segoe UI", 12),
                                     bg="#fff", justify="left", wraplength=780)
        self.output_label.pack(pady=8)

        tk.Label(self.right_frame, text=self.ui_texts["tts"][self.current_lang],
                 font=("Segoe UI", 13, "bold"), bg="#fff", fg="#333").pack(pady=(5, 0))

        frame_box = Frame(self.right_frame, bg="#ccc", highlightbackground="#666", highlightthickness=2)
        frame_box.pack(pady=6)
        self.text_input = tk.Text(frame_box, height=6, width=90, font=("Segoe UI", 12), bd=0)
        self.text_input.pack(padx=5, pady=5)
        self.text_input.insert("1.0", "Bu yerga matn kiriting...")

        tk.Button(self.right_frame, text="▶️ O‘qish", font=("Segoe UI", 14, "bold"),
                  bg="#b9fbc0", width=15, height=1, command=self.text_to_speech).pack(pady=6)

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def change_language(self, lang):
        self.current_lang = lang
        set_tts_voice_for_lang(lang)
        speak_async({"uz": "Til o‘zbekchaga o‘zgartirildi.",
                     "ru": "Язык изменён на русский.",
                     "en": "Language switched to English."}[lang])

    def start_camera(self):
        if self.cap:
            self.output_label.config(text="Kamera allaqachon ishlamoqda.")
            return
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            self.output_label.config(text="Kamera topilmadi.")
            speak_async("Kamera topilmadi.")
            self.cap = None
            return
        self.stop_camera = False
        self.output_label.config(text="Kamera ishga tushdi.")
        self.update_camera()

    def update_camera(self):
        if self.stop_camera:
            return
        ret, frame = self.cap.read()
        if not ret:
            self.root.after(100, self.update_camera)
            return

        results = yolo_model(frame, verbose=False)
        annotated = frame.copy()
        detected = set()

        for box in results[0].boxes:
            cls = int(box.cls[0])
            conf = float(box.conf[0])
            if conf < 0.5:
                continue
            name = results[0].names[cls]
            label = translations.get(name, name)
            detected.add(label)
            (x1, y1, x2, y2) = map(int, box.xyxy[0])
            cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(annotated, f"{label} ({conf:.2f})", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        if detected:
            names = ", ".join(detected)
            if names != self.last_detected:
                self.last_detected = names
                self.output_label.config(text=f"Aniqlangan obyektlar: {names}")
                speak_async(f"Rasmda {names} bor")

        img_rgb = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)
        cw, ch = self.canvas.winfo_width(), self.canvas.winfo_height()
        img_pil = ImageOps.fit(img_pil, (cw, ch), Image.Resampling.LANCZOS)
        img_tk = ImageTk.PhotoImage(img_pil)
        self.canvas.delete("all")
        self.canvas.create_image(cw / 2, ch / 2, anchor="center", image=img_tk)
        self.canvas.image = img_tk

        self.root.after(30, self.update_camera)

    def stop_camera_func(self):
        self.stop_camera = True
        if self.cap:
            self.cap.release()
            self.cap = None
        self.canvas.delete("all")
        self.output_label.config(text="Kamera to‘xtatildi.")
        speak_async("Kamera to‘xtatildi.")

    def open_image(self):
        path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.jpeg *.png *.bmp")])
        if not path:
            return
        img = cv2.imread(path)
        if img is None:
            self.output_label.config(text="Rasmni ochib bo‘lmadi.")
            return
        results = yolo_model(img, verbose=False)
        annotated = img.copy()
        detected = set()
        for box in results[0].boxes:
            cls = int(box.cls[0])
            conf = float(box.conf[0])
            if conf < 0.4:
                continue
            name = results[0].names[cls]
            label = translations.get(name, name)
            detected.add(label)
            (x1, y1, x2, y2) = map(int, box.xyxy[0])
            cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 200, 0), 2)
            cv2.putText(annotated, f"{label} {conf:.2f}", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        img_pil = Image.fromarray(cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB))
        cw, ch = self.canvas.winfo_width(), self.canvas.winfo_height()
        img_pil = ImageOps.fit(img_pil, (cw, ch), Image.Resampling.LANCZOS)
        img_tk = ImageTk.PhotoImage(img_pil)
        self.canvas.delete("all")
        self.canvas.create_image(cw / 2, ch / 2, anchor="center", image=img_tk)
        self.canvas.image = img_tk
        if detected:
            names = ", ".join(detected)
            self.output_label.config(text=f"Aniqlangan obyektlar: {names}")
            speak_async(f"Rasmda {names} bor")
        else:
            self.output_label.config(text="Rasmda obyekt topilmadi.")
            speak_async("Rasmda obyekt topilmadi.")

    def speech_to_text(self):
        lang = self.current_lang
        model_path = VOSK_MODELS.get(lang)
        if not model_path or not os.path.isdir(model_path):
            model_path = VOSK_MODELS.get("en")
        if not model_path or not os.path.isdir(model_path):
            self.output_label.config(text="VOSK modeli topilmadi.")
            return
        model = vosk.Model(model_path)
        rec = vosk.KaldiRecognizer(model, 16000)
        self.output_label.config(text="Gapiring...")
        speak_async("Iltimos, gapiring.")
        recording = sd.rec(int(5 * 16000), samplerate=16000, channels=1, dtype='int16')
        sd.wait()
        rec.AcceptWaveform(recording.tobytes())
        res = json.loads(rec.FinalResult())
        text = res.get("text", "")
        if text:
            self.output_label.config(text=f"Ovozdan matnga: {text}")
            speak_async(f"Siz {text} dedingiz!")
        else:
            self.output_label.config(text="Hech nima aniqlanmadi.")
            speak_async("Hech nima aniqlanmadi.")

    def text_to_speech(self):
        text = self.text_input.get("1.0", "end").strip()
        if not text or text.lower() == "bu yerga matn kiriting...":
            self.output_label.config(text="Matn kiritilmadi.")
            speak_async("Iltimos, matn kiriting.")
            return
        self.output_label.config(text=f"O‘qilmoqda: {text}")
        speak_async(text)

    def on_close(self):
        self.stop_camera = True
        if self.cap:
            self.cap.release()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = AIAssistantApp(root)
    root.mainloop()
