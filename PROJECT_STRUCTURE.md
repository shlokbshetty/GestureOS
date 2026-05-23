# Gesture Control Desktop Application - Project Structure

## Overview

This document describes the project directory structure for the Gesture Control Desktop Application.

## Directory Layout

```
gesture-control-desktop-app/
├── backend/                          # Python backend service
│   ├── __init__.py                   # Package initialization
│   ├── engine.py                     # Vision pipeline and gesture detection
│   ├── controller.py                 # Windows automation (keyboard, mouse, media)
│   ├── gesture_registry.py           # Gesture-to-action mapping
│   ├── state_manager.py              # Application lifecycle and state tracking
│   ├── api_server.py                 # FastAPI REST API and WebSocket
│   ├── main.py                       # Application entry point
│   ├── utils/                        # Utility modules
│   │   ├── __init__.py
│   │   ├── logger.py                 # Structured logging with rotation
│   │   ├── config.py                 # Configuration management
│   │   ├── debounce.py               # Cooldown and debounce system
│   │   └── smoothing.py              # Temporal smoothing algorithm
│   └── models/                       # ML models directory
│       ├── __init__.py
│       └── cnn_model_keras.h5        # Pre-trained CNN model (to be added)
│
├── frontend/                         # React frontend dashboard
│   ├── public/                       # Static assets
│   ├── src/
│   │   ├── components/               # React components
│   │   ├── pages/                    # Page components
│   │   ├── context/                  # React context (WebSocket, state)
│   │   ├── styles/                   # CSS/Tailwind styles
│   │   ├── App.tsx                   # Root component
│   │   └── index.tsx                 # Entry point
│   ├── package.json                  # Node dependencies
│   └── tsconfig.json                 # TypeScript configuration
│
├── desktop/                          # Electron/Tauri wrapper
│   ├── main.js                       # Electron main process
│   ├── preload.js                    # Preload script for IPC
│   ├── package.json                  # Electron dependencies
│   └── assets/                       # Application icons and assets
│
├── venv/                             # Python virtual environment
├── logs/                             # Application logs (created at runtime)
├── requirements.txt                  # Python dependencies
├── config.json                       # Application configuration
├── .env                              # Environment variables
├── .gitignore                        # Git ignore rules
└── README.md                         # Project documentation
```

## Key Files

### Backend

- **engine.py**: Core vision pipeline
  - GestureEngine class for camera capture and frame processing
  - SkinDetector class for YCrCb skin detection
  - CNN inference and temporal smoothing

- **controller.py**: Windows automation
  - WindowsController class for keyboard, mouse, and media key control
  - Action execution with error handling

- **gesture_registry.py**: Gesture mapping
  - GestureRegistry class for gesture-to-action mappings
  - Configuration loading and persistence

- **state_manager.py**: Application lifecycle
  - StateManager class for state machine and transitions
  - Cooldown tracking and action logging

- **api_server.py**: REST API
  - FastAPI application with REST endpoints
  - WebSocket streaming for real-time updates

- **main.py**: Application entry point
  - Component initialization and wiring
  - Signal handling for graceful shutdown

### Frontend

- **App.tsx**: Root React component
  - WebSocket connection management
  - Global state and styling

- **Dashboard.tsx**: Main dashboard layout
  - Three-column grid layout
  - Control, camera, and configuration panels

- **Components**: Reusable UI components
  - ControlPanel: Start/Stop/Pause/Resume buttons
  - GestureDisplay: Current gesture and confidence
  - CameraFeed: Live camera preview
  - ActionLog: Recent actions
  - ConfigPanel: Configuration controls
  - StatisticsPanel: Performance metrics

### Desktop

- **main.js**: Electron main process
  - Window creation and lifecycle
  - Backend process management
  - System tray integration

- **preload.js**: IPC communication
  - Secure communication between main and renderer processes

## Configuration Files

- **config.json**: Application configuration
  - Gesture mappings
  - Camera settings
  - Recognition parameters
  - Logging configuration

- **.env**: Environment variables
  - Backend host and port
  - Camera device ID
  - Model path
  - Logging level

- **requirements.txt**: Python dependencies
  - Core libraries (OpenCV, TensorFlow, FastAPI)
  - Development tools (pytest, black, flake8)

## Virtual Environment

The Python virtual environment is located in `venv/` and contains all Python dependencies.

### Activation

**Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
venv\Scripts\activate.bat
```

**Linux/macOS:**
```bash
source venv/bin/activate
```

### Installation

```bash
pip install -r requirements.txt
```

## Logs Directory

The `logs/` directory is created at runtime and contains:
- `app.log`: Main application log file
- Rotated log files (app.log.1, app.log.2, etc.)

## Getting Started

1. **Create virtual environment** (if not already done):
   ```bash
   python -m venv venv
   ```

2. **Activate virtual environment**:
   ```bash
   # Windows PowerShell
   .\venv\Scripts\Activate.ps1
   # Windows Command Prompt
   venv\Scripts\activate.bat
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run backend service**:
   ```bash
   python backend/main.py
   ```

5. **Run frontend** (in separate terminal):
   ```bash
   cd frontend
   npm install
   npm start
   ```

## Next Steps

- Implement core backend modules (engine, controller, state manager)
- Set up REST API server
- Create React frontend dashboard
- Package as Electron/Tauri desktop application
- Create Windows installer

## Requirements Mapping

This structure satisfies the following requirements:
- **Requirement 1.0**: Unified Gesture Recognition Engine
- **Requirement 5.0**: REST API Server
- **Requirement 14.0**: Desktop Application Packaging and Installation
