# GestureOS — Support & Troubleshooting (`SUPPORT.md`)

Need help configuring your webcam, tuning temporal smoothing, or debugging virtual HID shortcuts? Use the resources and troubleshooting steps below.

---

## 1. Support Channels

| Channel | Best For | Link / Location |
| :--- | :--- | :--- |
| **Documentation Suite** | Architecture, REST/WebSocket API, and local setup | [README.md](README.md), [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md), [docs/API.md](docs/API.md), [DEVELOPMENT.md](DEVELOPMENT.md) |
| **GitHub Issues (Bug Reports)** | Reproducible crashes, camera initialization bugs, or state machine errors | [`.github/ISSUE_TEMPLATE/bug_report.md`](.github/ISSUE_TEMPLATE/bug_report.md) |
| **GitHub Issues (Feature Requests)** | New OS actions, model enhancements, or UI widgets | [`.github/ISSUE_TEMPLATE/feature_request.md`](.github/ISSUE_TEMPLATE/feature_request.md) |
| **Security Advisories** | Private vulnerability reporting | [SECURITY.md](SECURITY.md) |

---

## 2. Issue Tracker Labels

When filing an issue on GitHub, apply the relevant label(s):
- `bug`: Unexpected runtime failure or state regression
- `enhancement`: New gesture class, OS action, or dashboard feature
- `vision-pipeline`: Issues relating to `SkinDetector`, `YCrCb` thresholds, or OpenCV camera capture
- `onnx-inference`: Issues relating to `OptimizedGestureModel` or `export_model.py`
- `windows-hid`: Issues relating to `WindowsController` (`pynput` / `pyautogui` shortcuts)
- `frontend-hud`: React 19 / Vite / WebSocket dashboard issues
- `documentation`: Improvements to markdown guides or SVG diagrams

---

## 3. Frequently Asked Questions (FAQs)

### Q1: `GestureEngine` logs `"No camera available (tried devices 0 and 1)"`. How do I run GestureOS without a webcam?
Launch GestureOS with the `--mock` flag:
```powershell
python run.py --mock
```
This initializes `MockGestureEngine` so you can explore the React dashboard, modify gesture configurations, and test all REST/WebSocket endpoints without camera hardware. If you do have a webcam, verify that Windows Privacy Settings (`Settings -> Privacy & security -> Camera`) allow desktop apps to access your camera and that no other application (e.g., Zoom, Teams, OBS) holds an exclusive lock on the device.

### Q2: Why does the engine fall back to `"heuristic"` inference mode?
`OptimizedGestureModel` (`backend/models/model_runner.py`) checks the configured `model_path` first and then `backend/models/gesture_model.onnx`. If `gesture_model.onnx` was deleted or `onnxruntime` is not installed, it falls back to lightweight heuristic mode. To rebuild the ONNX model and verify `onnxruntime`:
```powershell
pip install onnx>=1.15.0 onnxruntime>=1.16.0
python -m backend.models.export_model
```

### Q3: Gestures trigger too easily (false positives) or feel sluggish to confirm. How do I tune responsiveness?
Open the **Configuration Panel** in the React dashboard (`http://localhost:3000`) or send a `POST /api/config` request to adjust:
- **`confidence_threshold`** (default `0.70`): Increase toward `0.85` to require higher CNN certainty per frame.
- **`smoothing_frames`** (default `20` frames @ `30 FPS` = `~667 ms`): Reduce to `10-12` frames for faster response, or increase to `25-30` frames in noisy lighting environments.
- **`cooldown_ms`** per gesture: Increase (e.g., `1000 ms`) to prevent rapid repeat activations.

### Q4: `POST /api/start` returns `HTTP 409 Conflict`. Why?
The `StateManager` finite state machine only permits `start()` from the `stopped` state. If the engine is currently `running` or `paused`, call `POST /api/stop` (or `POST /api/resume` if `paused`) instead.

### Q5: Where are application logs stored?
All components log to `logs/app.log` via `StructuredLogger` (`backend/utils/logger.py`), which rotates automatically at `10 MB` and retains up to `5` backup files (`app.log.1` through `app.log.5`).
