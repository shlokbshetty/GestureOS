---
name: Bug Report
about: Report a reproducible bug in GestureOS vision pipeline, ONNX inference, Windows HID controller, or React HUD
title: "[BUG] <short descriptive summary>"
labels: ["bug"]
assignees: ""
---

## Bug Description

<!-- A clear and concise description of the bug. -->

## Affected Component

- [ ] Vision Pipeline & Camera Capture (`backend/engine.py`)
- [ ] ONNX Runtime / Model Runner (`backend/models/model_runner.py`)
- [ ] State Machine & Cooldowns (`backend/state_manager.py`)
- [ ] Windows Virtual HID Controller (`backend/controller.py`)
- [ ] FastAPI REST / WebSocket Server (`backend/api_server.py`)
- [ ] React 19 Frontend Dashboard (`frontend/`)
- [ ] Unified Launcher (`run.py`)

## Steps to Reproduce

1. Launch GestureOS with command: `python run.py ...`
2. Call endpoint / perform gesture / click UI control: `...`
3. Observe error: `...`

## Expected Behavior

<!-- Describe what should have happened. -->

## Actual Behavior

<!-- Describe what actually happened, including HTTP status codes or unintended OS actions. -->

## Logs & Screenshots

<!-- Paste relevant lines from `logs/app.log` or terminal output below: -->
```text
Paste logs/app.log output or stack trace here
```

## Environment Information

- **OS & Version**: (e.g., Windows 11 Pro 23H2)
- **Python Version**: (e.g., Python 3.12.4)
- **Node.js & npm Version**: (e.g., Node v20.14.0, npm 10.7.0)
- **Inference Backend (`onnx` / `keras` / `heuristic`)**:
- **Camera Hardware (or `--mock` mode)**:
