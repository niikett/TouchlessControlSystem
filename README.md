# Touchless Control System

A modular, gesture- and voice-controlled desktop interface that simulates an **AI Glasses HUD (Heads-Up Display)**. This project enables users to interact with applications using **hand gestures and voice commands**, eliminating the need for traditional input devices like a mouse or keyboard.

---

## Features

* **Hand Tracking & Gesture Control**

  * Cursor movement using hand tracking
  * Gestures for click, scroll, and interaction

* **Voice Command Engine**

  * Natural language command parsing
  * System control (volume, navigation, app switching)

* **HUD Interface**

  * Fullscreen, glasses-like UI
  * Modular screen system (Search, Maps, WhatsApp, Translate)

* **Integrated Modules**

  * Google Search
  * Maps Navigation
  * YouTube
  * WhatsApp Interaction
  * Spotify

* **System Controls**

  * Volume adjustment
  * Quick-open commands

# Hand Gesture Control System

The system enables **touchless interaction using real-time hand gestures**, allowing users to control the cursor, perform clicks, and scroll without a mouse.

It leverages **computer vision (MediaPipe)** to detect hand landmarks and translate them into system-level actions.

---

## Gesture Processing Pipeline

```
Camera Input
   ↓
Hand Tracking (MediaPipe)
   ↓
Landmark Detection (21 Points)
   ↓
Finger State Detection (Up/Down)
   ↓
Gesture Recognition
   ↓
Cursor Controller (PyAutoGUI)
   ↓
System Interaction
```

---

## Supported Gestures

| Gesture                | Finger State                      | Action      | Behavior        |
|------------------------|-----------------------------------|-------------|-----------------|
| Index Finger Movement  | Index finger up                   | Move        | Controls cursor |
| Pinch (Thumb + Index)  | Thumb + Index close               | Click       | Left click      |
| Pinch (Thumb + Middle) | Thumb + Middle close (Index down) | Right Click | Right click     |
| Two-Finger Gesture     | Index + Middle up                 | Scroll      | Scroll up/down  |

---

## Detailed Gesture Mapping

### Cursor Movement

| Condition             | Behavior                           |  
|-----------------------|------------------------------------|
| Index finger detected | Cursor follows finger position     |
| Default state         | Always active                      | 
| Smoothing applied     | Reduces jitter for stable movement |

**Key Points:**
- Maps camera coordinates → screen space
- Applies smoothing using moving average
- Constrains movement within screen boundaries

---

### Left Click (Pinch Gesture)

| Condition                              | Behavior                       |
|----------------------------------------|--------------------------------|
| Thumb + Index distance below threshold | Trigger left click             |
| Cooldown applied                       | Prevents multiple rapid clicks |

**Gesture:** Bring thumb and index finger together

---

### Right Click

| Condition            | Behavior                        | 
|----------------------|---------------------------------|
| Thumb + Middle close | Trigger right click             |
| Index finger down    | Avoids conflict with left click |
| Cooldown applied     | Prevents repeated triggers      |

---

### Scroll Gesture

| Condition                 | Behavior                  |
|---------------------------|---------------------------|
| Index + Middle fingers up | Enables scroll mode       |
| Vertical hand movement    | Controls scroll direction |
| Movement speed            | Controls scroll intensity |

**Key Points:**
- Uses vertical motion (Y-axis)
- Accumulates movement for smooth scrolling
- Filters noise using thresholding

---

## Gesture Priority System

To avoid conflicts, gestures are processed in priority order:

1. Scroll (highest priority)  
2. Left Click  
3. Right Click  
4. Move (default fallback)  

This ensures **stable and predictable interactions**.

---

## Technical Highlights

### Coordinate Mapping
- Converts camera input → screen coordinates
- Uses interpolation for accuracy
- Applies bounding constraints

### Smoothing Algorithm
- Moving average over recent positions
- Reduces jitter and noise
- Improves user experience

### Cooldown System
- Prevents rapid repeated clicks
- Ensures controlled interactions

### Scroll Accumulator
- Smooth scrolling behavior
- Avoids micro jitter
- Converts motion into usable scroll input

---

## Limitations

- Requires good lighting conditions
- Performance depends on camera quality
- Single-hand tracking only
- Depth perception is limited (2D tracking)

---

---

## Voice Command Reference

This system supports a wide range of natural language voice commands categorized by functionality.

### System Volume Controls

| Command Examples                            | Action   | Behavior                       |
| ------------------------------------------- | -------- | ------------------------------ |
| "volume up", "increase volume", "louder"    | Increase | Raises volume by 10%           |
| "volume down", "decrease volume", "quieter" | Decrease | Lowers volume by 10%           |
| "set volume to 70%"                         | Set      | Sets volume to specified level |
| "volume max / full"                         | Set      | Sets volume to 100%            |
| "volume half"                               | Set      | Sets volume to 50%             |
| "volume low / minimum"                      | Set      | Sets volume to low level       |
| "mute", "silence", "shut up"                | Mute     | Mutes system audio             |
| "unmute"                                    | Unmute   | Restores system audio          |

### Spotify Controls

| Command Examples         | Action   | Behavior              |
| ------------------------ | -------- | --------------------- |
| "play Believer"          | Play     | Plays requested track |
| "play song Shape of You" | Play     | Plays requested track |
| "pause", "pause music"   | Pause    | Pauses playback       |
| "resume", "resume music" | Resume   | Resumes playback      |
| "next song", "skip"      | Next     | Plays next track      |
| "previous song"          | Previous | Plays previous track  |
| "spotify volume 80"      | Volume   | Sets Spotify volume   |

> Default: "play <song>" uses Spotify unless YouTube is specified.

### YouTube Controls

| Command Examples               | Action     | Behavior           |
| ------------------------------ | ---------- | ------------------ |
| "play lofi music on youtube"   | Play       | Plays video        |
| "youtube play coding tutorial" | Play       | Plays video        |
| "search youtube for recipes"   | Search     | Searches videos    |
| "youtube search AI tools"      | Search     | Searches videos    |
| "pause youtube"                | Pause      | Pauses video       |
| "resume youtube"               | Resume     | Resumes video      |
| "fullscreen youtube"           | Fullscreen | Toggles fullscreen |

### Google Maps Controls

| Command Examples           | Action        | Behavior            |
| -------------------------- | ------------- | ------------------- |
| "directions to airport"    | Directions    | Shows route         |
| "navigate to office"       | Directions    | Starts navigation   |
| "take me to mall"          | Directions    | Shows route         |
| "find restaurants near me" | Nearby Search | Finds nearby places |
| "show hospitals nearby"    | Nearby Search | Finds nearby places |
| "start navigation"         | Start         | Begins navigation   |

### Google Search

| Command Examples           | Action | Behavior               |
| -------------------------- | ------ | ---------------------- |
| "search for AI tools"      | Search | Performs Google search |
| "google machine learning"  | Search | Performs search        |
| "look up Python tutorials" | Search | Performs search        |

> Queries with "near me" are handled by Maps.

### WhatsApp Messaging

| Command Examples             | Action | Behavior      |
| ---------------------------- | ------ | ------------- |
| "send message to John hello" | Send   | Sends message |
| "whatsapp Rahul hi"          | Send   | Sends message |
| "message Aman call me"       | Send   | Sends message |

### Application Launch

| Command Examples | Action   | Behavior            |
| ---------------- | -------- | ------------------- |
| "open youtube"   | Open App | Launches YouTube    |
| "launch spotify" | Open App | Launches Spotify    |
| "open maps"      | Open App | Launches Maps       |
| "open whatsapp"  | Open App | Launches WhatsApp   |
| "open google"    | Open App | Launches Search     |
| "go to home"     | Open App | Returns to main HUD |

### System Navigation

| Command Examples  | Action   | Behavior        |
| ----------------- | -------- | --------------- |
| "back", "go back" | Navigate | Previous screen |
| "exit"            | Navigate | Exit screen     |
| "go home"         | Navigate | Home screen     |

---

## Voice Processing Pipeline

```
User Speech
   ↓
Speech Recognition
   ↓
Command Parsing (Regex-based NLP)
   ↓
Command Execution
   ↓
UI Callback / System Control
   ↓
Text-to-Speech Feedback
```

---

## Project Structure

```
TouchlessControlSystem/
├── core/                  
│   ├── event_bus.py       
│   └── state_manager.py   
│
├── hand_tracking/        
│   ├── tracker.py
│   ├── cursor_controller.py
│   └── gesture_recognizer.py
│
├── voice/                
│   ├── listener.py
│   ├── command_parser.py
│   ├── command_executor.py
│   └── tts_engine.py
│
├── modules/              
│   ├── spotify_controller.py
│   └── google_search.py
│
├── metrics/               
│   ├── gesture_benchmark.py
│   ├── system_benchmark.py
│   ├── voice_benchmark.py
│   ├── formulas.txt
│   ├── plots/
│   │   ├── gesture_confusion_matrix.png
│   │   ├── system_performance.png
│   │   └── voice_confusion_matrix.png
│   └── test_data/
│       └── voice_test_cases.py
│
├── ui/                    
│   ├── main_window.py
│   ├── hand_tracker_overlay.py
│   ├── screens/
│   │   ├── maps_screen.py
│   │   ├── search_screen.py
│   │   ├── spotify_screen.py
│   │   ├── youtube_screen.py
│   │   └── whatsapp_screen.py
│   └── styles/
│       └── hud_theme.qss
│
├── utils/                 
│   └── system_controls.py
│
├── config.py              
├── main.py                
└── requirements.txt       
```

---

## Development Phases

| Phase | Description                     |
| ----- | ------------------------------- |
| 1     | Project scaffolding & structure |
| 2     | Hand tracking (cursor movement) |
| 3     | Gesture recognition             |
| 4     | GUI shell (HUD interface)       |
| 5     | Gesture + GUI integration       |
| 6     | Voice command engine            |
| 7     | Google Search integration       |
| 8     | Maps integration                |
| 9     | WhatsApp integration            |
| 10    | Spotify integration             |
| 10    | YouTube integration             |
| 11    | System controls via voice       |
| 12    | Quick-open voice commands       |
| 13    | Full integration testing        |
| 14    | UI polish & animations          |
| 15    | Demo & edge case handling       |

---


---

## Tech Stack

* Computer Vision: MediaPipe, OpenCV
* Automation: PyAutoGUI
* Voice Processing: SpeechRecognition, pyttsx3
* GUI Framework: PyQt5 / Tkinter
* Architecture: Event-driven modular design

---

## Installation

```bash
git clone https://github.com/niikett/TouchlessControlSystem.git
cd TouchlessControlSystem
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## Usage

```bash
python main.py
```

* Use hand gestures for cursor control
* Use voice commands for system interaction

---

## Known Limitations

* Performance depends on lighting and camera quality
* Voice recognition may vary based on environment
* Regex-based parsing limits flexibility

---

## Future Improvements

* AI-based NLP for better command understanding
* Cross-platform system controls
* Real-time performance optimization
* Translation module integration

---
