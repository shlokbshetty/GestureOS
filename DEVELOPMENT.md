# GestureOS — Developer Guide (`DEVELOPMENT.md`)

This guide covers setting up a local development environment, working with mock hardware fixtures, exporting ONNX models, training custom CNN classifiers, running the `pytest` test suite, and executing code quality linters.

---

## 1. Local Developer Environment Setup

### 1.1 System Requirements
- **Python**: `3.10`, `3.11`, or `3.12`
- **Node.js**: `18.0+` (with `npm` `9+`)
- **OS**: Windows 10/11 (for full `pywin32` and `pynput` HID testing) or Linux/macOS (for API, vision pipeline, and mock engine development)

### 1.2 Backend Setup
```powershell
# Create an isolated virtual environment
python -m venv .venv

# Activate on Windows PowerShell
.\.venv\Scripts\Activate.ps1

# Activate on Linux/macOS
# source .venv/bin/activate

# Install runtime and development dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### 1.3 Frontend Setup
```powershell
cd frontend
npm install
cd ..
```

### 1.4 Running in Development Mode
You can run the full stack via `run.py` or run the backend and frontend in separate terminals for granular debugging:

**Terminal 1 — FastAPI Backend (with Mock Vision Engine or Live Webcam):**
```powershell
# With live webcam and ONNX model:
python -m backend.main --host 127.0.0.1 --port 5000

# Without webcam hardware (MockGestureEngine):
python -m backend.main --host 127.0.0.1 --port 5000 --mock
```

**Terminal 2 — Vite React Dev Server (with HMR & API Proxy):**
```powershell
cd frontend
npm run dev -- --port 3000
```
Vite proxies all `/api/*` requests to `http://127.0.0.1:5000` and `/ws` connections to `ws://127.0.0.1:5000` (configured in `frontend/vite.config.ts`).

---

## 2. Dataset Preparation, Fixtures & Mock Modes

### 2.1 Hardware-Free Development (`MockGestureEngine`)
When developing on headless machines or CI runners without a physical webcam, pass `--mock` to `run.py` or `backend.main`. `MockGestureEngine` (`backend/main.py`) implements the full `GestureEngine` interface (`start()`, `stop()`, `register_callback()`, `get_frame_count()`, `confidence_threshold`, `smoothing_frames`) without initializing `cv2.VideoCapture`.

### 2.2 Rebuilding the ONNX Model Fixture
If `backend/models/gesture_model.onnx` is missing or you want to regenerate the deterministic ONNX Opset 17 graph:
```powershell
python -m backend.models.export_model
```
This script constructs `GestureRecognitionNet` (`[1, 1, 50, 50]` input -> `Conv2D(16)` -> `MaxPool` -> `Conv2D(32)` -> `MaxPool` -> `Flatten(4608)` -> `Gemm(64)` -> `Gemm(9)` -> `Softmax`), validates it with `onnx.checker.check_model()`, and writes `backend/models/gesture_model.onnx`.

### 2.3 Recording & Training Custom Gestures (`legacy-cnn-model/`)
The `legacy-cnn-model/` directory contains the original dataset collection and Keras training pipeline for the 9 gesture classes (`app_switch`, `close_window`, `nothing`, `play_pause`, `screenshot`, `scroll_down`, `scroll_up`, `volume_down`, `volume_up`), each stored as `1,200` grayscale `50x50` JPEG images under `legacy-cnn-model/gestures/<gesture_name>/`.

```powershell
cd legacy-cnn-model

# 1. Capture new 50x50 hand ROI frames via webcam
python create_gestures.py

# 2. Pack images into train_images, val_images, test_images pickles & label_map.pkl
python load_images.py

# 3. Train the 3-block Conv2D + BatchNorm + Dropout network for 50 epochs
python cnn_model_train.py
```
`cnn_model_train.py` outputs:
- `cnn_model_keras.h5` (best validation accuracy checkpoint)
- `training_history.png` (accuracy and cross-entropy loss curves)
- `confusion_matrix.png` (normalized 9x9 confusion matrix on the test split)

---

## 3. Testing Commands (`pytest` & Coverage)

GestureOS includes **200 unit and integration tests** across 10 test modules configured via `pytest.ini`:

```ini
[pytest]
pythonpath = . backend backend/utils
testpaths = backend
python_files = test_*.py
python_classes = Test*
python_functions = test_*
```

### 3.1 Execute Full Test Suite
```powershell
pytest
```

### 3.2 Execute Specific Test Modules
```powershell
# Vision pipeline, YCrCb skin segmentation, and temporal smoothing (44 tests)
pytest backend/test_engine.py -v

# FastAPI REST endpoints and WebSocket telemetry broadcast (7 tests)
pytest backend/test_api_server.py -v

# Windows virtual keyboard, media key, and mouse controller (31 tests)
pytest backend/test_controller.py -v

# GestureRegistry CRUD, validation, and JSON persistence (23 tests)
pytest backend/test_gesture_registry.py -v

# ApplicationState FSM transitions and cooldown enforcement (37 tests)
pytest backend/test_state_manager.py -v

# ConfigManager validation, dot-notation access, and RotatingFileHandler (47 tests)
pytest backend/utils/test_config.py backend/utils/test_logger.py -v

# Debouncer and CooldownTracker unit tests (4 tests)
pytest backend/utils/test_debounce.py -v

# TemporalSmoother ring buffer unit tests (4 tests)
pytest backend/utils/test_smoothing.py -v

# Main application orchestration and signal handling (3 tests)
pytest backend/test_main.py -v
```

### 3.3 Generate Test Coverage Reports
```powershell
# Terminal summary with missing line numbers
pytest --cov=backend --cov-report=term-missing

# Generate interactive HTML coverage report in htmlcov/
pytest --cov=backend --cov-report=html
```

---

## 4. Linting, Formatting & Type Checking

### 4.1 Python Code Quality (`black`, `flake8`, `mypy`)
All Python formatting and static analysis tools are pre-listed in `requirements.txt`:

```powershell
# Format backend and launcher code with Black
black backend/ run.py

# Check formatting without modifying files
black --check backend/ run.py

# Run Flake8 linter
flake8 backend/ run.py --max-line-length=100

# Run MyPy static type checker
mypy backend/ run.py --ignore-missing-imports
```

### 4.2 Frontend Code Quality (`oxlint` & TypeScript)
```powershell
cd frontend

# Run Oxlint static analyzer (.oxlintrc.json)
npm run lint

# Run TypeScript compiler typecheck
npx tsc -b --noEmit

# Verify production bundle compilation
npm run build
```

---

## 5. Logging & Diagnostics

GestureOS uses `StructuredLogger` (`backend/utils/logger.py`), which writes structured entries to both stdout (`INFO` and above) and `logs/app.log` (`DEBUG` and above) with automatic `10 MB` file rotation (`5` backup files kept):

```text
2026-10-28 22:15:04 - gesture_engine - INFO - Camera initialized and processing thread started
2026-10-28 22:15:06 - state_manager - INFO - Action executed: keyboard_shortcut (gesture: app_switch, confidence: 0.92)
```

To inspect live logs during development:
```powershell
Get-Content -Path "logs\app.log" -Wait -Tail 30
```
