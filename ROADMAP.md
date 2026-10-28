# GestureOS — Product Roadmap (`ROADMAP.md`)

This roadmap outlines the short-term engineering milestones, medium-term feature expansions, and long-term platform goals for **GestureOS**.

---

## Phase 1: Core Vision, ONNX Runtime & Web HUD (Completed — `v1.0.0`)
- [x] `YCrCb` chrominance skin segmentation (`SkinDetector`) with `5x5` elliptical morphological filtering.
- [x] Sub-millisecond ONNX Runtime inference engine (`OptimizedGestureModel`, `~0.19 ms` latency) with Keras `.h5` and heuristic fallbacks.
- [x] Thread-safe `StateManager` lifecycle FSM (`stopped`, `starting`, `running`, `pausing`, `paused`, `stopping`) and per-gesture `CooldownTracker`.
- [x] `WindowsController` virtual HID synthesis (`Alt+Tab`, `Alt+F4`, `Space`, `Volume Up/Down`, `Print Screen`, `Scroll Up/Down`).
- [x] FastAPI REST & WebSocket (`/ws`) telemetry gateway and React 19 + TypeScript HUD dashboard.
- [x] 200-test `pytest` suite and single-command `python run.py` launcher.

---

## Phase 2: Short-Term Milestones (`v1.1.0` — Q1)
- [ ] **Live Annotated MJPEG / WebRTC Camera Stream in HUD**:
  - Stream optional downsampled ROI preview and bounding-box overlays to `CameraHUD.tsx` so users can visually calibrate hand placement in real time.
- [ ] **Adaptive Skin Calibration Wizard**:
  - Add `POST /api/calibrate` endpoint that samples a `5-second` hand placement patch from the center reticle to dynamically tune `lower_cr`, `upper_cr`, `lower_cb`, and `upper_cb` in `SkinDetector` for extreme warm/cool ambient lighting.
- [ ] **Custom Keybinding & Macro Editor in UI**:
  - Extend `GestureCards.tsx` to allow interactive recording of arbitrary key combinations (e.g., `Ctrl+C`, `Win+D`, `Ctrl+Shift+Esc`) via `PUT /api/gestures/{gesture_name}`.
- [ ] **DirectML / CUDA Execution Provider Toggle**:
  - Expose `execution_provider` (`CPUExecutionProvider`, `DmlExecutionProvider`, `CUDAExecutionProvider`) in `config.json` and `OptimizedGestureModel`.

---

## Phase 3: Medium-Term Milestones (`v1.2.0` — Q2–Q3)
- [ ] **21-Point Hand Landmark Hybrid Pipeline**:
  - Combine lightweight palm/landmark keypoint extraction with the `50x50` ROI CNN classifier to support dynamic trajectory gestures (e.g., pinch-to-zoom, 2D cursor tracking, swipe left/right).
- [ ] **Application-Specific Gesture Profiles**:
  - Detect the active foreground window title via `pywin32` (`win32gui.GetWindowText(win32gui.GetForegroundWindow())`) and automatically switch `GestureRegistry` profiles (e.g., Presentation Mode for PowerPoint, Media Mode for VLC/Spotify, Browser Mode for Chrome).
- [ ] **System Tray Background Mode (`pystray`)**:
  - Integrate `pystray` system tray icon with quick Pause/Resume toggles and native Windows toast notifications when running in `--backend-only` headless mode.

---

## Phase 4: Long-Term Milestones (`v2.0.0` — Q4+)
- [ ] **In-Dashboard Few-Shot Gesture Trainer**:
  - Allow users to record 50 frames of a new custom hand pose directly inside the React dashboard and fine-tune the final `Gemm(64 -> N)` classification head on-device.
- [ ] **Cross-Platform Native Packaging (Tauri / Electron)**:
  - Bundle the Python ONNX backend (via PyInstaller) and the React 19 frontend into a single-click `.msi` installer for Windows and `.dmg` for macOS.
