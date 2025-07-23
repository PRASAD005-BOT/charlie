# 🤖 Charlie - AI Virtual Assistant

Charlie is an intelligent voice-controlled AI virtual assistant developed using Python. It performs a wide range of daily tasks — from opening applications and fetching weather updates to generating PowerPoint slides — all through simple voice commands.

---

## 🌟 Features

- 🎙️ **Voice Control:** Interact with Charlie using natural language.
- 🗣️ **Text-to-Speech (TTS):** Responds with human-like voice feedback.
- 🌐 **Web Interface:** A simple and elegant front-end built with Eel.
- 🧭 **Google Maps Integration:** Search locations, directions, and more.
- 🎶 **Spotify Playback:** Control music using voice.
- ☁️ **Weather Forecasting:** Get real-time weather updates.
- 📅 **Smart Scheduler:** Add weekly schedules with reminders.
- 🕹️ **Browser Game Launcher:** Play games like Subway Surfers or Temple Run.
- 📞 **Communication:** Send WhatsApp messages or make voice calls.
- 📊 **PowerPoint Generator:** Automatically create presentations via voice.
- 🌍 **Multilingual Support:** Easily configurable for multiple languages.
- 🤖 **Chatbot Mode:** Built-in fallback conversational engine.

---

## 📁 Project Structure

charlie/
├── engine/ # Core logic and task handlers
│ ├── alaram.py
│ ├── Googlemaps.py
│ ├── language.py
│ ├── schedule_module.py
│ ├── spotify.py
│ ├── weather.py
│ ├── powerpoint.py
│ ├── steering2.py
│ └── features.py
├── www/ # Web UI
│ ├── index.html
│ ├── style.css
│ ├── script.js
│ └── assets/ # Images, logos, and other static content
├── main.py # Main assistant controller
├── run.py # Alternate entry point
├── requirements.txt # Python dependencies
└── README.md # Project documentation

---

## ⚙️ Installation

### 🔁 1. Clone the Repository

```bash
git clone https://github.com/PRASAD005-BOT/charlie.git
cd charlie
2. Create and Activate Virtual Environment
<details> <summary>💻 Windows</summary>
bash
python -m venv envcharlie
.\envcharlie\Scripts\activate
python3 -m venv envcharlie
source envcharlie/bin/activate
pip install -r requirements.txt
python main.py
