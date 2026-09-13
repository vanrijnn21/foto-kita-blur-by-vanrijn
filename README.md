 # Peace Sign Blur - vanrjin

> Real-time hand gesture detection using MediaPipe and OpenCV.

RETROLENS is a computer vision project that detects the **✌️ peace sign gesture** through a webcam and automatically applies a blur effect to the camera feed.

The project uses **MediaPipe Hand Landmarker** for hand landmark detection and **OpenCV** for real-time camera processing and visual effects.

---

## ✨ Features

* 🎥 Real-time webcam processing
* ✋ Hand landmark detection with MediaPipe
* ✌️ Peace sign gesture recognition
* 🌫️ Automatic Gaussian blur effect
* ⚡ Real-time processing using MediaPipe `LIVE_STREAM`
* 🔄 Automatic MediaPipe model download
* 🪟 Simple OpenCV interface
* 💻 Windows camera backend support

---

## 🧠 How It Works

RETROLENS analyzes the user's hand through the webcam.

The program checks the position of specific hand landmarks to determine whether the following fingers are raised:

* Index finger → UP
* Middle finger → UP
* Ring finger → DOWN
* Pinky finger → DOWN

If the pattern matches a peace sign:

```text
✌️ Peace Sign
      ↓
Hand Landmark Detection
      ↓
Gesture Classification
      ↓
Peace Sign Confirmed
      ↓
Gaussian Blur
```

Otherwise, the camera feed remains normal.

The project also uses a small frame stabilizer to prevent the effect from rapidly switching on and off because of individual detection fluctuations.

---

## 🛠️ Technologies

| Technology | Purpose                                 |
| ---------- | --------------------------------------- |
| Python     | Main programming language               |
| OpenCV     | Webcam processing and visual effects    |
| MediaPipe  | Hand landmark detection                 |
| Threading  | Handling asynchronous detection results |

---

## 📋 Requirements

* Python 3.9+
* Webcam
* Internet connection on the first run
* Windows recommended

---

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/retrolens.git
cd retrolens
```

Replace `YOUR_USERNAME` with your GitHub username.

### 2. Create a virtual environment

Windows:

```bash
python -m venv .venv
```

Activate it:

```bash
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the application

```bash
python main.py
```

On the first run, RETROLENS automatically downloads the required MediaPipe hand landmark model.

---

## 🎮 Controls

| Key | Action           |
| --- | ---------------- |
| `Q` | Quit application |

### Gesture

| Gesture                        | Effect |
| ------------------------------ | ------ |
| ✌️ Peace Sign                  | Blur   |
| 🤚 Normal Hand / No Peace Sign | Normal |

---

## 📁 Project Structure

```text
RETROLENS/
│
├── main.py              # Main application
├── requirements.txt     # Python dependencies
├── README.md            # Project documentation
├── .gitignore           # Git ignored files
├── LICENSE              # Project license
│
└── assets/
    └── demo.png         # Optional project screenshot
```

---

## ⚙️ Configuration

Several parameters can be modified directly in `main.py`.

### Camera

```python
CAMERA_INDEX = 0
```

Change the value if your webcam uses another camera index.

Example:

```python
CAMERA_INDEX = 1
```

### Display Resolution

```python
DISPLAY_WIDTH = 720
DISPLAY_HEIGHT = 405
```

### Gesture Stabilization

```python
PEACE_REQUIRED_FRAMES = 3
NORMAL_REQUIRED_FRAMES = 3
```

These values control how many consecutive frames are required before the application changes its current state.

---

## 🔐 Model Handling

RETROLENS does not require the MediaPipe model to be manually placed in the repository.

The application checks whether:

```text
hand_landmarker.task
```

exists locally.

If the model is missing, it downloads the official model automatically and validates the downloaded file before using it.

This keeps the repository lightweight.

---

## 🧪 Current Status

**Status: Working Prototype**

The current version focuses on:

* Real-time hand detection
* Peace sign recognition
* Camera blur effect
* Stable gesture state switching
* Automatic model management

---

## 🔮 Future Improvements

Potential improvements include:

* [ ] Add more hand gestures
* [ ] Add configurable visual effects
* [ ] Add gesture-based filters
* [ ] Improve gesture classification accuracy
* [ ] Add GUI controls
* [ ] Add FPS counter
* [ ] Add configuration file
* [ ] Add screenshot/video demo
* [ ] Support additional operating systems

---

## 📚 References

* MediaPipe Hand Landmarker
* OpenCV Documentation
* Python Documentation

---

## 👨‍💻 Author

**Ediii**

Computer Vision & AI learning project.

---

## 📄 License

This project is licensed under the MIT License.

See [`LICENSE`](LICENSE) for details.
