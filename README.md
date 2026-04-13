# 🖐 Virtual Mouse using Hand Tracking

Control your computer mouse using hand gestures through your webcam.
This project uses **MediaPipe**, **OpenCV**, and **PyAutoGUI** to detect hand landmarks and convert them into real-time mouse actions.

---

## 🚀 Features

* 🎯 Move cursor using index finger
* 👆 Left click with index + thumb pinch
* 👉 Right click with middle + thumb pinch
* 🔼 Scroll up/down using two fingers
* 📸 Take screenshot using fist gesture
* ⚡ Smooth cursor movement with filtering
* 🧠 Real-time hand tracking using MediaPipe

---

## 🛠 Technologies Used

* Python
* OpenCV
* MediaPipe
* PyAutoGUI
* NumPy

---

## 📂 Project Structure

```bash
virtual-mouse/
│── main.py
│── requirements.txt
│── README.md
│── .gitignore
```

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/virtual-mouse.git
cd virtual-mouse
```

### 2. Create virtual environment (recommended)

```bash
python -m venv venv
source venv/bin/activate   # Linux / Mac
venv\Scripts\activate      # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## ▶️ Run the Project

```bash
python main.py
```

---

## 🎮 Controls / Gestures

| Gesture                 | Action      |
| ----------------------- | ----------- |
| Index finger            | Move cursor |
| Index + Thumb (close)   | Left click  |
| Middle + Thumb (close)  | Right click |
| Index + Middle (spread) | Scroll up   |
| Index + Middle (close)  | Scroll down |
| Fist (all fingers down) | Screenshot  |

---

## 🧠 How It Works

1. Webcam captures video frames
2. MediaPipe detects 21 hand landmarks
3. Finger positions are converted into pixel coordinates
4. Gestures are recognized using distance & finger states
5. PyAutoGUI controls the system mouse

---

## ⚡ Performance Tips

* Ensure good lighting for better detection
* Keep hand within camera frame
* Adjust sensitivity and thresholds in code if needed

---

## 📌 Future Improvements

* Multi-hand support
* Gesture customization
* GUI for settings
* AI-based gesture recognition

---

## 👨‍💻 Author

**Your Name**
GitHub: https://github.com/javidmushtan

---

## ⭐ Support

If you like this project, give it a ⭐ on GitHub!
