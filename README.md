# GestureOS: AI-Powered Gesture Control Desktop Platform

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen?style=for-the-badge&logo=githubactions&logoColor=white)](https://github.com/shlokbshetty/GestureOS)
[![Tests](https://img.shields.io/badge/Tests-200%2F200_Passing-success?style=for-the-badge&logo=pytest&logoColor=white)](pytest.ini)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104%2B-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![ONNX Runtime](https://img.shields.io/badge/ONNX_Runtime-0.19ms_Latency-005CED?style=for-the-badge&logo=onnx&logoColor=white)](https://onnxruntime.ai/)
[![React](https://img.shields.io/badge/React-19-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-6.0-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)

**GestureOS** is a low-latency computer vision desktop platform that transforms standard webcam video streams into hands-free operating system automation. Powered by an OpenCV YCrCb skin-segmentation pipeline, a sub-millisecond ONNX Runtime Convolutional Neural Network (`<0.2 ms` inference time per frame), a thread-safe application lifecycle state machine, a FastAPI REST and WebSocket telemetry server, and a glassmorphic React 19 + TypeScript HUD dashboard, GestureOS dispatches virtual keyboard, media, and mouse scroll events on Windows with configurable multi-frame temporal smoothing and per-gesture cooldown protection.

---

## High-Level System Architecture

![GestureOS System Architecture](docs/assets/system-overview.svg)

GestureOS is architected around four decoupled tiers:
1. **Optical Capture & Vision Preprocessing (`backend/engine.py`)**: Captures `640x480` BGR frames at `30 FPS` via OpenCV, isolates the hand Region of Interest (ROI) in `YCrCb` color space (`Cr: 130-170`, `Cb: 77-127`) with `5x5` elliptical morphological filtering, and extracts a padded `50x50` grayscale crop.
2. **ML Inference & Model Layer (`backend/models/`)**: Executes forward passes through `OptimizedGestureModel` (`gesture_model.onnx`, ONNX Opset 17) in `~0.19 ms` on CPU, with automatic fallback to Keras (`cnn_model_keras.h5`) or heuristic pixel-variance classification.
3. **Core Orchestration & Persistence (`backend/state_manager.py`, `backend/gesture_registry.py`, `backend/api_server.py`)**: Enforces multi-frame unanimous temporal smoothing (`default: 20 frames`), manages lifecycle transitions (`stopped`, `starting`, `running`, `pausing`, `paused`, `stopping`), tracks per-gesture cooldown timers, persists configuration to `config.json`, and streams real-time events over WebSocket (`/ws`).
4. **Presentation & Virtual HID Tier (`backend/controller.py`, `frontend/`)**: Dispatches native keyboard shortcuts (`Alt+Tab`, `Alt+F4`), media keys (`Volume Up/Down`, `Space`), and mouse wheel scrolls (`+200` / `-200` units) via `pynput`, while rendering live telemetry in a React 19 + Vite dashboard.

For an exhaustive breakdown of component boundaries, state machine transitions, and concurrency models, see **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** (also available at **[ARCHITECTURE.md](ARCHITECTURE.md)**).

---

## Gesture-to-Action Mapping Matrix

| Gesture ID | Display Name | Action Type | Default Parameters | Cooldown | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `app_switch` | **App Switch** | `keyboard_shortcut` | `{"keys": ["alt", "tab"]}` | `500 ms` | Switch between open applications |
| `close_window` | **Close Window** | `keyboard_shortcut` | `{"keys": ["alt", "F4"]}` | `500 ms` | Close current active window |
| `play_pause` | **Play/Pause** | `keyboard_key` | `{"key": "space"}` | `300 ms` | Toggle media playback |
| `volume_up` | **Volume Up** | `media_key` | `{"key": "volume_up"}` | `200 ms` | Increase system audio volume |
| `volume_down` | **Volume Down** | `media_key` | `{"key": "volume_down"}` | `200 ms` | Decrease system audio volume |
| `scroll_up` | **Scroll Up** | `mouse_scroll` | `{"units": 200}` | `100 ms` | Scroll active viewport upward |
| `scroll_down` | **Scroll Down** | `mouse_scroll` | `{"units": -200}` | `100 ms` | Scroll active viewport downward |
| `screenshot` | **Screenshot** | `keyboard_key` | `{"key": "print"}` | `1000 ms` | Capture full-screen screenshot |
| `nothing` | **No Gesture** | `none` | `{}` | `0 ms` | Idle state (no action dispatched) |

---

## Prerequisites

- **Operating System**: Windows 10 / 11 (64-bit recommended for native `pywin32` and `pynput` virtual HID hooks; Linux/macOS supported for API/mock development)
- **Python**: `3.10`, `3.11`, or `3.12`
- **Node.js & npm**: Node.js `18.0+` (`20+` recommended) and `npm` `9+`
- **Hardware**: Integrated or USB webcam capable of `640x480 @ 30 FPS` (optional when using `--mock` mode)

---

## Step-by-Step Local Setup

### 1. Clone the Repository
```bash
git clone https://github.com/shlokbshetty/GestureOS.git
cd GestureOS
```

### 2. Configure the Python Virtual Environment
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Install Frontend Dependencies
```powershell
cd frontend
npm install
cd ..
```

---

## Build, Training, Inference & Execution Commands

### Unified One-Command Product Launch
The root `run.py` orchestrator starts the FastAPI backend (`127.0.0.1:5000`), polls `/api/status` until healthy, launches the Vite dev server (`localhost:3000`), and opens your default browser:
```powershell
# Standard launch with live webcam + ONNX inference + React dashboard
python run.py

# Hardware-free mock engine mode (for CI, headless servers, or UI testing)
python run.py --mock

# Launch only the FastAPI backend on a custom port
python run.py --backend-only --port 5000

# Launch only the React frontend dashboard
python run.py --frontend-only --frontend-port 3000

# Launch full stack without auto-opening the browser
python run.py --no-browser
```

### Direct Backend Service Execution
```powershell
python -m backend.main --host 127.0.0.1 --port 5000 --config config.json --model backend/models/gesture_model.onnx
```

### Exporting & Benchmarking the ONNX Model
```powershell
# Deterministically build and verify backend/models/gesture_model.onnx (Opset 17)
python -m backend.models.export_model

# Benchmark ONNX Runtime inference latency over 100 iterations
python -c "from backend.models.model_runner import OptimizedGestureModel; m = OptimizedGestureModel('backend/models/gesture_model.onnx'); print(f'Avg latency: {m.benchmark(100):.3f} ms')"
```

### Legacy CNN Dataset Capture & Model Training
To record custom gesture datasets and train a Keras `.h5` model from scratch:
```powershell
cd legacy-cnn-model
python create_gestures.py
python load_images.py
python cnn_model_train.py
cd ..
```

### Frontend Production Build & Linting
```powershell
cd frontend
npm run lint      # Runs oxlint static analysis
npm run build     # Runs tsc -b && vite build -> outputs to frontend/dist/
npm run preview   # Previews production bundle locally
```

### Running the Test Suite
```powershell
# Run all 200 unit and integration tests
pytest

# Run with coverage report
pytest --cov=backend --cov-report=term-missing
```

---

## Configuration Mapping (`config.json`)

GestureOS reads and persists runtime settings to `config.json` in the repository root. Both `ConfigManager` (`backend/utils/config.py`) and `GestureRegistry` (`backend/gesture_registry.py`) validate this schema:

| JSON Path | Type | Default | Constraints | Description |
| :--- | :--- | :--- | :--- | :--- |
| `application.name` | `string` | `"Gesture Control Desktop"` | Non-empty string | Application display title |
| `application.version` | `string` | `"1.0.0"` | SemVer string | Release version identifier |
| `application.debug` | `boolean` | `false` | `true` / `false` | Enables verbose debug diagnostics |
| `camera.device_id` | `integer` | `0` | `>= 0` | OpenCV camera index (falls back to `1` if `0` fails) |
| `camera.fps` | `integer` | `30` | `1 - 120` | Target capture frame rate |
| `camera.resolution.width` | `integer` | `640` | Positive int | Capture width in pixels |
| `camera.resolution.height` | `integer` | `480` | Positive int | Capture height in pixels |
| `gesture_recognition.confidence_threshold` | `float` | `0.70` | `0.0 - 1.0` | Minimum softmax probability required to accept a frame prediction |
| `gesture_recognition.smoothing_frames` | `integer` | `20` | `1 - 100` | Consecutive unanimous frames required to confirm a gesture |
| `gesture_recognition.default_cooldown_ms` | `integer` | `500` | `0 - 5000` | Fallback cooldown duration in milliseconds |
| `logging.level` | `string` | `"INFO"` | `DEBUG`, `INFO`, `WARNING`, `ERROR` | Console and file logger threshold |
| `logging.directory` | `string` | `"logs"` | Valid directory path | Directory for rotating log files |
| `logging.file` | `string` | `"app.log"` | Filename | Active log filename |
| `logging.max_size_bytes` | `integer` | `10485760` | Bytes (`10 MB`) | Maximum size per log file before rotation |
| `logging.backup_count` | `integer` | `5` | `>= 1` | Number of rotated backup log files retained |
| `model.path` | `string` | `"backend/models/cnn_model_keras.h5"` | File path | Target model path (auto-resolves to `backend/models/gesture_model.onnx` if `.h5` is absent) |
| `model.input_size` | `integer` | `50` | `50` | Square spatial dimension (`50x50`) for CNN input |
| `model.normalize_range` | `array` | `[0, 1]` | `[min, max]` | Pixel intensity normalization bounds |
| `gestures.<name>.action` | `string` | Varies | `keyboard_shortcut`, `keyboard_key`, `media_key`, `mouse_scroll`, `none` | Virtual HID action primitive |
| `gestures.<name>.params` | `object` | Varies | Key/Scroll dictionary | Action parameters (`keys`, `key`, or `units`) |
| `gestures.<name>.cooldown_ms` | `integer` | `0 - 1000` | `>= 0` | Per-gesture refractory period in milliseconds |
| `gestures.<name>.enabled` | `boolean` | `true` | `true` / `false` | Whether the gesture triggers OS actions |

---

## Documentation Index

- **[Architecture Guide](docs/ARCHITECTURE.md)** ([Root Mirror](ARCHITECTURE.md))
- **[API & WebSocket Reference](docs/API.md)** ([Root Mirror](API.md))
- **[Developer Setup & Testing Guide](DEVELOPMENT.md)**
- **[Contributing Guidelines](CONTRIBUTING.md)**
- **[Roadmap](ROADMAP.md)** & **[Architectural Vision](VISION.md)**
- **[Security Policy](SECURITY.md)** & **[Support Guide](SUPPORT.md)**
- **[Changelog](CHANGELOG.md)**

---

## License

Released under the **MIT License**.
