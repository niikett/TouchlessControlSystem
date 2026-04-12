# 🧠 Touchless Control System (AI Glasses Interface)

A modular, gesture- and voice-controlled desktop interface that simulates an **AI Glasses HUD (Heads-Up Display)**. This project enables users to interact with applications using **hand gestures and voice commands**, eliminating the need for traditional input devices like a mouse or keyboard.

---

## 🚀 Features

* ✋ **Hand Tracking & Gesture Control**

  * Cursor movement using hand tracking
  * Gestures for click, scroll, and interaction

* 🎙️ **Voice Command Engine**

  * Natural language command parsing
  * System control (volume, navigation, app switching)

* 🖥️ **HUD Interface**

  * Fullscreen, glasses-like UI
  * Modular screen system (Search, Maps, WhatsApp, Translate)

* 🌐 **Integrated Modules**

  * Google Search
  * Maps Navigation
  * WhatsApp Interaction
  * Live Translation

* ⚙️ **System Controls**

  * Volume adjustment
  * Quick-open commands

---

## 🏗️ Project Structure

```
TouchlessControlSystem/
├── core/                  # Core architecture components
│   ├── event_bus.py       # Event-driven communication
│   └── state_manager.py   # Global state handling
│
├── hand_tracking/         # Gesture & tracking logic
│   ├── tracker.py
│   ├── cursor_controller.py
│   └── gesture_recognizer.py
│
├── voice/                 # Voice processing system
│   ├── listener.py
│   ├── command_parser.py
│   ├── command_executor.py
│   └── tts_engine.py
│
├── modules/               # Functional modules
│   └── google_search.py
│
├── ui/                    # GUI layer
│   ├── main_window.py
│   ├── screens/
│   │   ├── maps_screen.py
│   │   ├── search_screen.py
│   │   ├── translate_screen.py
│   │   └── whatsapp_screen.py
│   └── styles/
│       └── hud_theme.qss
│
├── utils/                 # System utilities
│   └── system_controls.py
│
├── config.py              # Configuration settings
├── main.py                # Entry point
└── requirements.txt       # Dependencies
```

---

## 🧩 Architecture Overview

```
AI GLASSES INTERFACE (HUD UI)
│
├── Application Modules
│   ├── WhatsApp
│   ├── Google Search
│   ├── Maps
│   └── Translation
│
├── Voice Command Engine
│   ├── Speech Recognition
│   └── Command Parsing & Execution
│
├── Touchless Control System
│   ├── Hand Tracking
│   ├── Gesture Recognition
│   └── Cursor Control
│
└── Core Layer
    ├── Event Bus
    └── State Management
```

---

## ⚙️ Tech Stack

* **Computer Vision:** MediaPipe, OpenCV
* **Automation:** PyAutoGUI
* **Voice Processing:** SpeechRecognition, TTS Engine
* **GUI Framework:** PyQt5 / Tkinter
* **Architecture:** Event-driven modular design

---

## 📦 Installation

1. Clone the repository:

```bash
git clone https://github.com/your-username/TouchlessControlSystem.git
cd TouchlessControlSystem
```

2. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

---

## ▶️ Usage

Run the application:

```bash
python main.py
```

* Use your **hand to control the cursor**
* Perform gestures for interaction
* Use **voice commands** to open modules and control the system

---

## 🎯 Development Phases

| Phase | Description                     |
| ----- | ------------------------------- |
| 1     | Project scaffolding & structure |
| 2     | Hand tracking (cursor movement) |
| 3     | Gesture recognition             |
| 4     | GUI shell (HUD interface)       |
| 5     | Gesture + GUI integration       |
| 6     | Voice command engine            |
| 7     | Google Search module            |
| 8     | Maps module                     |
| 9     | WhatsApp integration            |
| 10    | Live Translation                |
| 11    | System controls via voice       |
| 12    | Quick-open voice commands       |
| 13    | Full integration testing        |
| 14    | UI polish & animations          |
| 15    | Demo & edge case handling       |

---

## 🎬 Demo Flow

1. **Launch Application**

   * HUD interface appears with status indicators

2. **Gesture Control**

   * Move cursor with hand
   * Pinch → Click
   * Gesture → Scroll

3. **Voice Commands**

   * `"Open Maps"` → Navigation screen
   * `"Search hospital near me"`
   * `"Directions to Palladium Mall"`

4. **WhatsApp Module**

   * `"Open WhatsApp"`

5. **System Control**

   * `"Volume 50%"`
   * `"Mute"`

6. **Navigation**

   * `"Go Home"` → Return to main HUD

7. **Exit**

   * Press `ESC`

---

## 🧠 Key Concepts

* Event-driven architecture for decoupled modules
* Real-time gesture recognition pipeline
* Voice + gesture hybrid interaction model
* Modular UI system for scalability

---

## ⚠️ Known Limitations

* Performance depends on camera quality and lighting
* Voice recognition accuracy may vary
* Platform-dependent system controls

---

