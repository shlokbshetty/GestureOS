# Contributing to GestureOS

Thank you for your interest in contributing to **GestureOS**! We welcome contributions across computer vision preprocessing, ONNX model optimization, Windows virtual HID automation, FastAPI telemetry endpoints, and the React 19 dashboard.

---

## 1. Branching Conventions

All work must be performed on a dedicated topic branch branched off `main`. Use one of the following prefixes:

- `feat/<short-slug>`: New features (e.g., `feat/directml-gpu-provider`, `feat/custom-hotkey-remapping`)
- `fix/<short-slug>`: Bug fixes (e.g., `fix/ycrcb-contour-padding`, `fix/websocket-reconnect-cleanup`)
- `perf/<short-slug>`: Latency or memory optimizations (e.g., `perf/onnx-int8-quantization`)
- `docs/<short-slug>`: Documentation, SVG diagrams, or API spec updates
- `test/<short-slug>`: Adding or refactoring `pytest` or frontend test cases
- `chore/<short-slug>`: Dependency upgrades, build configuration, or tooling maintenance

---

## 2. Conventional Commits Guidelines

We enforce the [Conventional Commits v1.0.0](https://www.conventionalcommits.org/) specification:

```text
<type>(<scope>): <concise imperative summary>

[optional body explaining the "why" and architectural trade-offs]

[optional footer(s): Closes #123, BREAKING CHANGE: ...]
```

### Supported Scopes
- `engine`: `backend/engine.py` (`SkinDetector`, `GestureEngine`)
- `models`: `backend/models/` (`OptimizedGestureModel`, `export_model.py`, `gesture_model.onnx`)
- `controller`: `backend/controller.py` (`WindowsController`)
- `state`: `backend/state_manager.py` (`StateManager`, `ApplicationState`)
- `registry`: `backend/gesture_registry.py` (`GestureRegistry`)
- `api`: `backend/api_server.py` (`APIServer`, REST & `/ws`)
- `utils`: `backend/utils/` (`config.py`, `debounce.py`, `smoothing.py`, `logger.py`)
- `frontend`: `frontend/` (React 19 components, hooks, Vite config)
- `launcher`: `run.py` or `backend/main.py`

### Examples
- `feat(models): add DirectML execution provider fallback to OptimizedGestureModel`
- `fix(state): release RLock while awaiting in-flight action completion on stop()`
- `docs(api): document PUT /api/gestures/{gesture_name} 404 error payload`

---

## 3. Pull Request Lifecycle

1. **Fork & Branch**: Create a feature/fix branch from the latest `main`.
2. **Implement & Test**:
   - Write clean, thread-safe Python (`RLock` where state is shared across threads) and strictly typed TypeScript (`frontend/src/types.ts`).
   - Add unit tests in `backend/test_*.py` or `backend/utils/test_*.py` covering both happy paths and edge cases.
3. **Run Pre-Commit Verification Checks** (see Section 4 below).
4. **Open a Pull Request**: Complete all sections of `.github/PULL_REQUEST_TEMPLATE.md`.
5. **Code Review & Merge**: Address reviewer feedback; once all checks pass and a maintainer approves, the PR will be squash-merged into `main`.

---

## 4. Required Pre-Commit Checks

Before submitting a Pull Request, run the following commands from the repository root and verify zero failures:

```powershell
# 1. Run the complete 200-test pytest suite
pytest

# 2. Verify Python formatting and lint rules
black --check backend/ run.py
flake8 backend/ run.py --max-line-length=100
mypy backend/ run.py --ignore-missing-imports

# 3. Verify Frontend linting and TypeScript compilation
cd frontend
npm run lint
npm run build
cd ..
```

---

## 5. Code of Conduct

Participation in the GestureOS community is governed by our [Contributor Covenant Code of Conduct](.github/CODE_OF_CONDUCT.md).
