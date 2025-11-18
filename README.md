README.md — AI Yordamchi
Yordamchi SI

Sun’iy intellekt asosida rasm, ovoz va matn bilan ishlovchi desktop dastur

Bu loyiha Python tilida yozilgan bo‘lib, foydalanuvchiga 3 ta asosiy imkoniyatni taqdim etadi:

Kamera orqali obyektlarni aniqlash (YOLOv8)

Rasmdagi obyekt va matnni o‘qish (YOLO + Tesseract OCR)

Ovozdan matn olish (VOSK — offline STT)

Matnni ovozda o‘qish (pyttsx3 — offline TTS)

Dastur to‘liq oflayn ishlaydi.

Asosiy funksiyalar
Kamera orqali obyekt aniqlash

Kamera ochiladi

YOLOv8 modeli orqali real vaqt rejimida obyektlar taniladi

Tanilgan obyekt nomi ekranga va ovoz orqali aytiladi

Rasm yuklab obyekt va matnni o‘qish

Har qanday rasm (*.jpg, *.png, .jpeg) yuklanadi

YOLO yordamida obyektlar aniqlanadi

Tesseract OCR yordamida rasm ichidagi matn chiqariladi

Ovozdan matnga (Offline)

VOSK modeli yordamida internet bo‘lmasdan nutq matnga aylantiriladi

O‘zbek / Rus / Ingliz modellarni qo‘llab-quvvatlaydi

Matndan ovozga (Offline)

Kiritilgan matn pyttsx3 orqali ovozda o‘qib beriladi

Foydalanilgan texnologiyalar
Texnologiya	Vazifasi
Python 3.x	Dastur tili
Tkinter	Grafikli interfeys
YOLOv8	Obyekt aniqlash
OpenCV	Kamera va rasm bilan ishlash
Tesseract OCR	Rasm ichidagi matnni aniqlash
VOSK	Offline STT (ovozdan matnga)
pyttsx3	Offline TTS (matndan ovozga)
Pillow	Tasvirlar bilan ishlash
⚙️ O‘rnatish (Installation)
1️⃣ Loyihani yuklab oling
git clone https://github.com/username/Yordamchi SI.git
cd Yordamchi SI

2️⃣ Kerakli kutubxonalarni o‘rnating
pip install -r requirements.txt

3️⃣ Modellarni joylashtiring

models/ papkasiga quyidagilarni qo‘ying:

vosk-model-small-en-us-0.15
https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip

vosk-model-small-ru-0.22
https://alphacephei.com/vosk/models/vosk-model-small-ru-0.22.zip

vosk-model-small-uz-0.1
https://alphacephei.com/vosk/models/vosk-model-small-uz-0.1.zip

yolov8n.pt
https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt

4️⃣ Tesseract OCR o‘rnating

Windows uchun:

https://github.com/UB-Mannheim/tesseract/wiki

O‘rnagan manzilni kodda yangilang:

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

▶️ Dastur ishga tushirish
python Yordamchi SI.py

📁 Loyihaning tuzilishi
Yordamchi SI/
│── models/
│   ├── vosk-model-small-uz-0.1/
│   ├── vosk-model-small-en-us-0.15/
    ├── vosk-model-small-ru-0.22/
│── yolov8n.pt
│── images/
│── AI_Assistant.py
│── requirements.txt
│── README.md
│── LICENSE

Loyiha maqsadi

Ushbu loyiha kurs ishim uchun, sun’iy intellekt kutubxonalari bilan ishlashni amalda o‘rganish uchun yaratilgan. Junior darajadagi AI, CV va STT/TTS texnologiyalari bir dasturda birlashtirilgan.

Litsenziya

Loyiha MIT License asosida tarqatiladi.
Istagan inson o‘zgartirib, kengaytirib yoki ishlatishi mumkin.
