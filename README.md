# GestureOS: Computer Vision Desktop Automation Platform

[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.8.0%2B-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)](https://opencv.org/)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.14%2B-FF6F00?style=for-the-badge&logo=tensorflow&logoColor=white)](https://tensorflow.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104%2B-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PyAutoGUI](https://img.shields.io/badge/Automation-PyAutoGUI%20%7C%20Pynput-blue?style=for-the-badge)](https://pyautogui.readthedocs.io/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](LICENSE)

> **Real-time computer vision human-computer interface translating camera-captured hand kinematic gestures into zero-latency operating system automation events and virtual input streams.**

---

## Architecture & Data Flow Diagram

```mermaid
graph TD
    subgraph VideoCaptureTier ["Optical Sensor & Frame Acquisition"]
        Webcam["USB / Integrated Webcam Sensor"]
        OpenCVStream["OpenCV High-Speed Frame Stream (cv2.VideoCapture)"]
        YCrCb["Color Space Normalization & Skin Segmentation (YCrCb)"]
    end

    subgraph InferenceEngine ["Vision Recognition Engine"]
        ROIExtract["Adaptive ROI Contour & Bounding Box"]
        CNN["Pre-Trained 2D-CNN Classifier (TensorFlow/Keras)"]
        Registry["Gesture Registry & Confidence Threshold Evaluator"]
    end

    subgraph OrchestrationTier ["Controller & State Coordinator"]
        Controller["Workflow Controller (controller.py)"]
        StateMgr["Temporal State Machine & Debounce Engine (state_manager.py)"]
        ConfigLog["Hierarchical Config & Structured Logging"]
    end

    subgraph AutomationTier ["OS Automation & Virtual HID"]
        VirtualHID["Virtual Input Dispatcher (PyAutoGUI / Pynput)"]
        SysEvents["OS Window Switching, Volume Control & Smooth Scroll"]
        Tray["System Tray Daemon (PyStray / PyWin32)"]
    end

    subgraph TelemetryGateway ["API & Network Streaming"]
        FastAPI["FastAPI / WebSocket Telemetry Gateway"]
        WebUI["Desktop / Web Diagnostic Monitor"]
    end

    Webcam --> OpenCVStream
    OpenCVStream --> YCrCb
    YCrCb --> ROIExtract
    ROIExtract --> CNN
    CNN --> Registry

    Registry --> Controller
    Controller <--> StateMgr
    Controller --> ConfigLog

    Controller --> VirtualHID
    VirtualHID --> SysEvents
    Controller --> Tray

    Controller -.->|Real-Time Coordinates & FPS| FastAPI
    FastAPI --> WebUI
```

---

## Core Features

- **Real-Time Morphological Kinematic Tracking**: High-throughput optical frame parsing leveraging YCrCb chroma-subsampling and morphological filtering to segment hand regions under diverse ambient lighting.
- **Deep CNN Gesture Classification**: Multi-class deep convolutional network capable of distinguishing static and dynamic hand poses with high precision and sub-20ms inference latency.
- **Adaptive Debounce & Temporal State Engine**: Temporal windowing algorithm preventing accidental multi-triggering, ensuring smooth gesture transitions and stable gesture lock.
- **Direct OS-Level Hardware Synthesis**: Direct dispatch into Windows user32/pywin32 event loops, supporting smooth scroll velocity, system audio step adjustments, screenshot captures, and active application cycling.
- **Extensible Gesture-Action Registry**: Declarative JSON mapping matrix enabling users to dynamically customize key combinations, hotkeys, and shell macros mapped to individual gestures.
- **Asynchronous Telemetry Stream**: Integrated FastAPI WebSocket and REST server streaming live confidence levels, recognized gesture states, and framerate telemetry to desktop dashboards.

---

## Tech Stack Directory

| Layer | Technologies |
| :--- | :--- |
| **Computer Vision Core** | OpenCV (4.8+), NumPy, Pillow, YCrCb Segmentation Engine |
| **Machine Learning Core** | TensorFlow 2.14+, Keras Deep Learning Framework |
| **OS Automation & HID** | PyAutoGUI, Pynput, PyStray, PyWin32 Win32 API Bindings |
| **Service & Telemetry** | FastAPI, Uvicorn, WebSockets, Pydantic v2 |
| **Testing & Quality** | Pytest, Pytest-Cov, Flake8, Black, MyPy Static Type Checker |

---

## Quickstart & Verification

### Prerequisites
- **Python**: `3.10` or higher
- **Webcam**: Standard USB or built-in webcam
- **OS**: Windows 10/11 (Optimized for Win32 API; Linux/macOS compatible)

### Environment Configuration
Copy `.env.example` (or generate `.env`) from configuration defaults:

```env
# Runtime Environment
LOG_LEVEL=INFO
CAMERA_INDEX=0
DETECTION_CONFIDENCE_THRESHOLD=0.85
DEBOUNCE_INTERVAL_SECONDS=0.5

# Telemetry Server
API_HOST=127.0.0.1
API_PORT=8080
```

### Installation & Execution
```bash
# 1. Initialize and activate virtual environment
python -m venv venv
.\venv\Scripts\activate

# 2. Install core vision and automation libraries
pip install -r requirements.txt

# 3. Execute unit and regression test suite
pytest -v backend/

# 4. Launch the gesture recognition controller daemon
python -m backend.controller
```

---

## API & Service Specification

| Protocol | Route / Channel | Direction | Payload Schema | Functional Action |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/health` | Inbound | None | Verify camera acquisition loop and model health |
| `GET` | `/api/gestures` | Inbound | None | Fetch all registered gesture definitions and bindings |
| `POST` | `/api/gestures/map`| Inbound | `{ gesture_id: str, action: str }` | Dynamically override gesture keyboard shortcut mapping |
| `WS` | `/ws/telemetry` | Bidirectional | Continuous JSON: `{ fps, gesture, confidence }` | Real-time optical inference streaming to UI clients |
| `POST` | `/api/controller/toggle` | Inbound | `{ enabled: boolean }` | Pause or resume physical HID input interception |
