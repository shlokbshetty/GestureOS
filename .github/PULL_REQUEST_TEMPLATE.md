## Summary of Changes

<!-- Provide a concise summary of what this Pull Request accomplishes and why it is needed. -->

## Related Issues

<!-- Link related issues using keywords, e.g., Closes #42, Fixes #19 -->
- Closes #

## Type of Change

- [ ] `feat`: New feature (vision pipeline, ONNX runner, OS controller action, REST/WS endpoint, or React UI widget)
- [ ] `fix`: Bug fix (non-breaking change that resolves an issue)
- [ ] `perf`: Performance or latency improvement (e.g., ONNX Runtime / OpenCV optimization)
- [ ] `refactor`: Code restructuring with no behavioral change
- [ ] `docs`: Documentation or architecture diagram update
- [ ] `test`: Addition or update of `pytest` or frontend tests
- [ ] `chore`: Build scripts, dependencies, or tooling update
- [ ] `BREAKING CHANGE`: Change that modifies existing REST payloads, WebSocket events, or `config.json` schema

## Affected Subsystems

- [ ] Vision Pipeline (`backend/engine.py`, `SkinDetector`, `GestureEngine`)
- [ ] ML Inference & Models (`backend/models/model_runner.py`, `export_model.py`, `gesture_model.onnx`)
- [ ] State Machine & Registry (`backend/state_manager.py`, `backend/gesture_registry.py`)
- [ ] Windows HID Automation (`backend/controller.py`)
- [ ] FastAPI & WebSocket Server (`backend/api_server.py`)
- [ ] Utilities (`backend/utils/config.py`, `debounce.py`, `smoothing.py`, `logger.py`)
- [ ] React 19 Dashboard (`frontend/`)
- [ ] Unified Launcher (`run.py`, `backend/main.py`)

## Test Coverage & Verification

- [ ] All existing `pytest` suites pass (`pytest` -> 200+ passing)
- [ ] Added unit/integration tests for new backend logic
- [ ] Verified in `--mock` mode (`python run.py --mock`)
- [ ] Verified with live webcam & ONNX inference (if applicable)
- [ ] Frontend builds cleanly (`cd frontend && npm run lint && npm run build`)

## Self-Review Checklist

- [ ] Thread-shared state is properly synchronized (`threading.RLock()`)
- [ ] Code adheres to `black` and `flake8` formatting rules
- [ ] Documentation (`README.md`, `docs/API.md`, `docs/ARCHITECTURE.md`, `CHANGELOG.md`) has been updated to reflect any public API or configuration changes
- [ ] No hardcoded user paths, credentials, or raw dataset binaries were committed
