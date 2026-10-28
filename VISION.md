# GestureOS — Architectural Vision (`VISION.md`)

## 1. Mission Statement

**GestureOS** envisions a zero-friction, touchless human-computer interaction layer where any standard consumer webcam acts as a deterministic, sub-millisecond spatial command sensor—empowering users to navigate windows, control media, and automate workflows without physical contact with a keyboard or mouse.

---

## 2. Core Architectural Pillars

### Pillar 1: Sub-Millisecond Edge Execution
Touchless interfaces fail when perceptual latency exceeds `50 ms` or when background CPU utilization degrades foreground applications. By compiling our convolutional feature extractor into a static ONNX Opset 17 graph (`backend/models/gesture_model.onnx`) and executing it via ONNX Runtime with full graph fusion (`ORT_ENABLE_ALL`), GestureOS completes neural inference in **`~0.19 ms`** per frame (`>5,000 FPS` theoretical throughput). Even at a continuous `30 FPS` capture rate, neural inference consumes less than `0.6%` of a single CPU core's wall-clock time.

### Pillar 2: Zero False-Positive Ergonomics
In an operating system controller, a single false positive—such as accidentally triggering `Alt+F4` (`close_window`) during casual hand movement—destroys user trust. GestureOS solves the precision-recall trade-off through a **three-stage verification gate**:
1. **Morphological Chrominance Gating (`SkinDetector`)**: Filters out non-skin backgrounds and contours smaller than `100 px^2` before the neural network is ever invoked.
2. **Per-Frame Softmax Thresholding (`confidence_threshold = 0.70`)**: Rejects ambiguous hand transitions and low-certainty frames as `nothing`.
3. **Unanimous Ring-Buffer Consensus (`TemporalSmoother`) & Per-Gesture Refractory Cooldowns (`CooldownTracker`)**: Requires `N` (`20`) consecutive frames to unanimously agree on the same gesture class before emitting a single `gesture_detected` event, followed immediately by a buffer reset and a gesture-specific cooldown (`100 ms` to `1,000 ms`).

### Pillar 3: Strict Decoupling & Observable Telemetry
Rather than coupling webcam capture directly to OS key synthesis in a monolithic loop (as in early prototypes like `legacy-cnn-model/final.py`), GestureOS separates **Perception** (`GestureEngine`), **Policy & Lifecycle** (`StateManager` + `GestureRegistry`), **Actuation** (`WindowsController`), and **Presentation** (`APIServer` + React 19 HUD). Every internal transition is observable in real time over WebSockets (`/ws`) and auditable via rotating structured logs (`logs/app.log`).

### Pillar 4: Privacy by Design (100% Local Processing)
Cameras are deeply personal sensors. GestureOS guarantees that optical data never leaves the local process memory: frames are captured, segmented into `50x50` grayscale arrays, classified on-device, and immediately discarded.

---

## 3. Long-Term Evolution

As GestureOS evolves toward `v2.0`, the architecture is designed to transition seamlessly from **discrete static pose classification** (9 fixed classes) to **context-aware continuous spatial computing**:
- **Foreground Context Awareness**: Dynamically remapping the 9 gesture slots based on the active OS window (e.g., IDE debugging shortcuts vs. media playback vs. slide deck navigation).
- **On-Device Personalization**: Enabling users to adapt both the skin chrominance envelope (`YCrCb`) and the final linear classification layer (`Gemm`) to their own lighting environment and hand anatomy in seconds.
