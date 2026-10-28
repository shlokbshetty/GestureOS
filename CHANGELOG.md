# Changelog

All notable changes to **GestureOS** are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [v1.0.0] - 2026-10-28

### Added
- **Sub-Millisecond ONNX Runtime Engine (`backend/models/model_runner.py`, `backend/models/export_model.py`)**:
  - Added `OptimizedGestureModel` achieving `~0.19 ms` inference latency on CPU (`ORT_ENABLE_ALL`) with automatic fallback to TensorFlow/Keras (`.h5`) and heuristic variance/intensity classification.
  - Added deterministic ONNX Opset 17 model exporter (`create_onnx_gesture_model`) generating `backend/models/gesture_model.onnx` (`1x1x50x50` input -> 9 gesture classes).
- **Real-Time Vision Pipeline (`backend/engine.py`)**:
  - Implemented `SkinDetector` using `YCrCb` chrominance thresholding (`Cr: 130-170`, `Cb: 77-127`), `5x5` elliptical morphological close/open filtering, largest-contour bounding box extraction, and `10 px` ROI padding.
  - Implemented `GestureEngine` daemon capture loop at `30 FPS` (`640x480`) with automatic camera device fallback (`0 -> 1`) and unanimous multi-frame temporal smoothing.
- **Application Lifecycle State Machine (`backend/state_manager.py`)**:
  - Added thread-safe `StateManager` with `ApplicationState` FSM (`stopped`, `starting`, `running`, `pausing`, `paused`, `stopping`), per-gesture cooldown tracking, graceful in-flight action drain on `stop()`, and a 1,000-entry action history ring buffer.
- **Centralized Gesture Registry & Config Manager (`backend/gesture_registry.py`, `backend/utils/config.py`)**:
  - Added `GestureRegistry` supporting 9 core gestures (`app_switch`, `close_window`, `play_pause`, `volume_up`, `volume_down`, `scroll_up`, `scroll_down`, `screenshot`, `nothing`) with runtime JSON persistence.
  - Added `ConfigManager` with dot-notation getters/setters and strict schema validation (`ConfigurationError`).
- **Windows Virtual HID Automation (`backend/controller.py`)**:
  - Implemented `WindowsController` wrapping `pynput` keyboard and mouse controllers for multi-key shortcuts (`Alt+Tab`, `Alt+F4`), single keys (`Space`, `Print Screen`), media keys (`Volume Up`, `Volume Down`), and mouse scrolling (`+200` / `-200` units).
- **FastAPI REST & WebSocket Telemetry Server (`backend/api_server.py`)**:
  - Added 12 REST endpoints (`/api/status`, `/api/start`, `/api/stop`, `/api/pause`, `/api/resume`, `/api/config`, `/api/gestures`, `/api/gestures/{gesture_name}`, `/api/logs`, `/api/camera-status`) and a thread-safe WebSocket broadcast hub (`/ws`).
- **Glassmorphic React 19 + TypeScript Dashboard (`frontend/`)**:
  - Built modular HUD with `Header`, `CameraHUD`, `ControlPanel`, `GestureCards`, `ConfigPanel`, `ActionLogFeed`, and auto-reconnecting `useWebSocket` hook.
- **Unified Launcher & Comprehensive Test Suite (`run.py`, `backend/test_*.py`)**:
  - Added single-command product bootstrapper (`python run.py`) with `--mock`, `--backend-only`, `--frontend-only`, and `--no-browser` modes.
  - Added 200 passing `pytest` unit and integration tests across 10 test modules.

### Changed
- Migrated from the standalone legacy OpenCV + Keras desktop script (`legacy-cnn-model/final.py`) to a decoupled client-server architecture with ONNX Runtime and FastAPI WebSocket streaming.
- Replaced single-frame raw CNN predictions with `TemporalSmoother` (`backend/utils/smoothing.py`) and `CooldownTracker` (`backend/utils/debounce.py`) to eliminate false triggers.

### Deprecated
- Direct execution of `legacy-cnn-model/final.py` for desktop control is deprecated in favor of `python run.py` and `backend/main.py` (retained in `legacy-cnn-model/` for dataset collection and historical benchmarking).

### Security
- Bound FastAPI server to `127.0.0.1` by default and restricted `WindowsController` key synthesis to an explicit key map allowlist.
