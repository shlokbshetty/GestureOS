# GestureOS - Project Structure

## Overview

This document describes the complete enterprise project directory structure for GestureOS.

## Directory Layout

```
GestureOS/
├── backend/                              # Python backend service
│   ├── __init__.py                       # Package initialization
│   ├── engine.py                         # Vision pipeline, skin detection & inference
│   ├── controller.py                     # Windows virtual keyboard/mouse automation
│   ├── gesture_registry.py               # Gesture-to-action configuration store
│   ├── state_manager.py                  # Application lifecycle and state tracking
│   ├── api_server.py                     # FastAPI REST API & WebSocket server
│   ├── main.py                           # Backend application entry point
│   ├── models/                           # AI/ML models & inference runners
│   │   ├── __init__.py
│   │   ├── export_model.py               # Optimized ONNX model exporter
│   │   └── model_runner.py               # Sub-millisecond ONNX Runtime engine
│   ├── utils/                            # Utility modules
│   │   ├── __init__.py
│   │   ├── config.py                     # Configuration management
│   │   ├── debounce.py                   # Cooldown and debounce system
│   │   ├── logger.py                     # Structured rotating file logging
│   │   └── smoothing.py                  # Temporal smoothing algorithm
│   ├── test_api_server.py                # REST & WebSocket endpoint test suite
│   ├── test_controller.py                # Windows automation test suite
│   ├── test_engine.py                    # Vision pipeline & camera test suite
│   ├── test_gesture_registry.py          # Gesture registry test suite
│   ├── test_main.py                      # Application orchestration test suite
│   └── test_state_manager.py             # State machine test suite
│
├── frontend/                             # React frontend dashboard
│   ├── index.html                        # Application entry HTML
│   ├── package.json                      # Node dependencies & build scripts
│   ├── tsconfig.json                     # TypeScript configuration
│   ├── vite.config.ts                    # Vite dev server & backend proxy
│   └── src/
│       ├── App.tsx                       # Root dashboard orchestrator
│       ├── main.tsx                      # React root entry
│       ├── index.css                     # Glassmorphic design system
│       ├── types.ts                      # Shared TypeScript data models
│       ├── components/                   # UI components
│       │   ├── Header.tsx                # Status badges, latency, & camera status
│       │   ├── ControlPanel.tsx          # Start/Stop/Pause buttons & metrics
│       │   ├── CameraHUD.tsx             # Live tracking reticle & confidence bar
│       │   ├── GestureCards.tsx          # 9 interactive gesture cards
│       │   ├── ActionLogFeed.tsx         # Real-time action stream
│       │   └── ConfigPanel.tsx           # Dynamic sliders & gesture toggles
│       ├── hooks/
│       │   └── useWebSocket.ts           # Auto-reconnecting WebSocket client
│       └── services/
│           └── api.ts                    # REST API client
│
├── legacy-cnn-model/                     # Original training assets & legacy scripts
│   ├── cnn_model_train.py                # Historical training script
│   ├── label_map.pkl                     # Class index map
│   └── gestures/                         # Dataset samples
│
├── config.json                           # Application configuration
├── pytest.ini                            # Unified test runner configuration
├── requirements.txt                      # Python dependencies
├── run.py                                # Single-command product launcher
└── README.md                             # Product documentation
```

## Key Modules

### Vision Pipeline & AI
- **`backend/engine.py`**:
  - `SkinDetector`: YCrCb color space thresholding and morphological cleanup.
  - `GestureEngine`: Real-time camera capture loop @ 30 FPS, temporal smoothing, and event dispatch.
- **`backend/models/model_runner.py`**:
  - `OptimizedGestureModel`: High-speed ONNX Runtime execution (<0.2ms latency) with automatic DirectML/CPU acceleration and fallback heuristics.
- **`backend/models/export_model.py`**:
  - Builds and exports the optimized ONNX model graph directly to `gesture_model.onnx`.

### Windows Automation & State
- **`backend/controller.py`**:
  - `WindowsController`: Cross-platform virtual HID automation using `pynput` and `pyautogui` for shortcuts (`Alt+Tab`, `Alt+F4`), media keys (`Volume Up/Down`), and mouse scrolling.
- **`backend/gesture_registry.py`**:
  - `GestureRegistry`: Centralized registry of 9 supported gestures, metadata, and JSON persistence.
- **`backend/state_manager.py`**:
  - `StateManager`: Application state machine (`stopped`, `starting`, `running`, `paused`, `stopping`), cooldown enforcement, and action logging.

### Telemetry & Web Interface
- **`backend/api_server.py`**:
  - `APIServer`: FastAPI application with REST endpoints (`/api/status`, `/api/start`, `/api/stop`, `/api/config`, `/api/logs`) and WebSocket streaming (`/ws`).
- **`frontend/src/`**:
  - Modern React 18 + Vite interface with glassmorphism design, real-time HUD, and dynamic configuration controls.
