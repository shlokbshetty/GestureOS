# GestureOS — API & WebSocket Reference (`API.md`)

GestureOS exposes a RESTful HTTP API and a real-time bidirectional WebSocket telemetry stream powered by **FastAPI** (`backend/api_server.py`), alongside modular **Python APIs** for vision inference, state management, and OS automation.

---

## 1. Base URLs & Authentication

| Interface | Default Local URL | Vite Dev Proxy Path | Authentication |
| :--- | :--- | :--- | :--- |
| **REST API Base URL** | `http://127.0.0.1:5000` | `http://localhost:3000/api` | None (Localhost loopback service with CORS enabled) |
| **WebSocket Endpoint** | `ws://127.0.0.1:5000/ws` | `ws://localhost:3000/ws` | None |
| **OpenAPI Swagger UI** | `http://127.0.0.1:5000/docs` | N/A | None |
| **ReDoc Specification** | `http://127.0.0.1:5000/redoc` | N/A | None |

---

## 2. REST API Endpoints

### 2.1 `GET /api/status`
Retrieves the current application lifecycle state, active gesture, most recent executed action, uptime in seconds, and total action count.

- **Request Parameters**: None
- **Response (`200 OK`)**:
```json
{
  "state": "running",
  "current_gesture": "app_switch",
  "last_action": {
    "gesture": "app_switch",
    "action": "keyboard_shortcut",
    "confidence": 0.92,
    "timestamp": 1729875600.12,
    "success": true
  },
  "uptime_seconds": 124.53,
  "total_actions": 18,
  "timestamp": 1729875600.15
}
```
- **Error Responses**:
  - `500 Internal Server Error`: `{"detail": "<error message>"}`

---

### 2.2 `POST /api/start`
Transitions the application state machine from `stopped` -> `starting` -> `running` and initializes the webcam capture thread.

- **Request Body**: None
- **Response (`200 OK`)**:
```json
{
  "success": true,
  "state": "running"
}
```
- **Error Responses**:
  - `409 Conflict`: Returned if the engine is not currently in the `stopped` state or if the camera hardware fails to open.
    ```json
    {
      "detail": "Cannot start from state 'running'"
    }
    ```
  - `500 Internal Server Error`: `{"detail": "<error message>"}`

---

### 2.3 `POST /api/stop`
Transitions the application from `running` or `paused` -> `stopping` -> `stopped`, waits up to 5 seconds for in-flight OS actions to complete, and releases the webcam device.

- **Request Body**: None
- **Response (`200 OK`)**:
```json
{
  "success": true,
  "state": "stopped"
}
```
- **Error Responses**:
  - `500 Internal Server Error`: `{"detail": "<error message>"}`

---

### 2.4 `POST /api/pause`
Temporarily suspends gesture interception (`running` -> `pausing` -> `paused`) without releasing the camera resource.

- **Request Body**: None
- **Response (`200 OK`)**:
```json
{
  "success": true,
  "state": "paused"
}
```
- **Error Responses**:
  - `409 Conflict`:
    ```json
    {
      "detail": "Cannot pause from state 'stopped'"
    }
    ```

---

### 2.5 `POST /api/resume`
Resumes gesture recognition from a `paused` state (`paused` -> `running`).

- **Request Body**: None
- **Response (`200 OK`)**:
```json
{
  "success": true,
  "state": "running"
}
```
- **Error Responses**:
  - `409 Conflict`:
    ```json
    {
      "detail": "Cannot resume from state 'stopped'"
    }
    ```

---

### 2.6 `GET /api/config`
Returns the active gesture registry map, confidence threshold, and temporal smoothing window size.

- **Request Parameters**: None
- **Response (`200 OK`)**:
```json
{
  "gestures": {
    "app_switch": {
      "action": "keyboard_shortcut",
      "params": { "keys": ["alt", "tab"] },
      "cooldown_ms": 500,
      "enabled": true,
      "display_name": "App Switch",
      "icon": "app_switch.svg",
      "description": "Switch between open applications"
    },
    "volume_up": {
      "action": "media_key",
      "params": { "key": "volume_up" },
      "cooldown_ms": 200,
      "enabled": true,
      "display_name": "Volume Up",
      "icon": "volume_up.svg",
      "description": "Increase volume"
    }
  },
  "confidence_threshold": 0.70,
  "smoothing_frames": 20
}
```

---

### 2.7 `POST /api/config`
Dynamically updates `confidence_threshold`, `smoothing_frames`, and/or multiple gesture configurations at runtime. Validated by Pydantic model `ConfigUpdateRequest`.

- **Request Schema (`ConfigUpdateRequest`)**:
  - `confidence_threshold` (`float`, optional): `0.0 <= value <= 1.0`
  - `smoothing_frames` (`int`, optional): `1 <= value <= 100`
  - `gestures` (`Dict[str, Dict[str, Any]]`, optional): Map of gesture names to partial field updates.
- **Example Request Body**:
```json
{
  "confidence_threshold": 0.80,
  "smoothing_frames": 25,
  "gestures": {
    "volume_up": {
      "cooldown_ms": 250,
      "enabled": true
    }
  }
}
```
- **Response (`200 OK`)**:
```json
{
  "success": true,
  "config": {
    "gestures": { "...": "..." },
    "confidence_threshold": 0.80,
    "smoothing_frames": 25
  }
}
```
- **Error Responses**:
  - `422 Unprocessable Entity`: Returned automatically by FastAPI when `confidence_threshold` is outside `[0.0, 1.0]` or `smoothing_frames` is outside `[1, 100]`.
  - `500 Internal Server Error`: `{"detail": "<error message>"}`

---

### 2.8 `GET /api/gestures`
Returns the dictionary of all 9 registered gestures and their metadata from `GestureRegistry`.

- **Request Parameters**: None
- **Response (`200 OK`)**: Dictionary mapping each gesture ID (`app_switch`, `close_window`, `play_pause`, `volume_up`, `volume_down`, `scroll_up`, `scroll_down`, `screenshot`, `nothing`) to its metadata object.

---

### 2.9 `PUT /api/gestures/{gesture_name}`
Updates a single gesture's configuration and persists the change to `config.json`. Validated by Pydantic model `GestureUpdateRequest`.

- **Path Parameter**:
  - `gesture_name` (`str`, required): Identifier of the gesture (e.g., `app_switch`, `scroll_up`).
- **Request Schema (`GestureUpdateRequest`)**:
  - `action` (`str`, optional)
  - `params` (`Dict[str, Any]`, optional)
  - `cooldown_ms` (`int`, optional, `>= 0`)
  - `enabled` (`bool`, optional)
  - `display_name` (`str`, optional)
  - `description` (`str`, optional)
- **Example Request Body**:
```json
{
  "enabled": false,
  "cooldown_ms": 600
}
```
- **Response (`200 OK`)**:
```json
{
  "success": true,
  "gesture": {
    "display_name": "App Switch",
    "icon": "app_switch.svg",
    "description": "Switch between open applications",
    "cooldown_ms": 600,
    "enabled": false
  }
}
```
- **Error Responses**:
  - `404 Not Found`:
    ```json
    {
      "detail": "Gesture 'unknown_gesture' not found"
    }
    ```
  - `422 Unprocessable Entity`: If `cooldown_ms < 0`.

---

### 2.10 `GET /api/logs`
Returns recent executed action log entries in reverse chronological order (newest first).

- **Query Parameters**:
  - `limit` (`int`, optional, default `100`): Maximum number of log entries to return.
- **Response (`200 OK`)**:
```json
[
  {
    "gesture": "volume_up",
    "action": "media_key",
    "confidence": 0.94,
    "timestamp": 1729875612.41,
    "success": true
  },
  {
    "gesture": "app_switch",
    "action": "keyboard_shortcut",
    "confidence": 0.89,
    "timestamp": 1729875600.12,
    "success": true
  }
]
```

---

### 2.11 `DELETE /api/logs`
Clears the in-memory `StateManager` action history ring buffer.

- **Request Parameters**: None
- **Response (`200 OK`)**:
```json
{
  "success": true,
  "message": "Action logs cleared"
}
```

---

### 2.12 `GET /api/camera-status`
Returns real-time camera hardware connectivity, capture loop status, target FPS, per-frame ONNX inference latency in milliseconds, and total processed frame count.

- **Request Parameters**: None
- **Response (`200 OK`)**:
```json
{
  "connected": true,
  "running": true,
  "fps_target": 30,
  "inference_latency_ms": 0.19,
  "frame_count": 3480
}
```

---

## 3. WebSocket Telemetry Protocol (`ws://127.0.0.1:5000/ws`)

Upon connecting to `/ws`, the client is registered in `APIServer.websocket_clients` and immediately receives a `connection_established` snapshot. All server-pushed packets share the envelope schema:

```ts
interface WebSocketEvent {
  type: 'connection_established' | 'gesture_detected' | 'state_changed' | 'action_executed' | 'action_failed' | 'camera_error' | 'pong';
  data?: any;
  timestamp: number;
}
```

### 3.1 Server-to-Client Broadcast Events

#### `connection_established`
Sent immediately upon WebSocket handshake completion:
```json
{
  "type": "connection_established",
  "data": {
    "state": "running",
    "current_gesture": "nothing",
    "last_action": null,
    "uptime_seconds": 12.4,
    "total_actions": 0,
    "timestamp": 1729875600.0
  },
  "timestamp": 1729875600.0
}
```

#### `gesture_detected`
Emitted by `GestureEngine` when a gesture passes temporal smoothing:
```json
{
  "type": "gesture_detected",
  "data": {
    "gesture": "scroll_down",
    "confidence": 0.91,
    "timestamp": 1729875605.32
  },
  "timestamp": 1729875605.32
}
```

#### `state_changed`
Emitted by `StateManager` on any `ApplicationState` transition:
```json
{
  "type": "state_changed",
  "data": {
    "old_state": "stopped",
    "new_state": "starting",
    "timestamp": 1729875601.05
  },
  "timestamp": 1729875601.05
}
```

#### `action_executed` / `action_failed`
Emitted by `WindowsController` when an OS HID action succeeds or raises an exception:
```json
{
  "type": "action_executed",
  "data": {
    "action": "keyboard_shortcut"
  },
  "timestamp": 1729875610.11
}
```

#### `camera_error`
Emitted by `GestureEngine` if webcam initialization fails:
```json
{
  "type": "camera_error",
  "data": {
    "message": "No camera available (tried devices 0 and 1)"
  },
  "timestamp": 1729875602.0
}
```

### 3.2 Client-to-Server Heartbeat Messages
Clients may send a JSON heartbeat ping at any time:
```json
{ "type": "ping" }
```
The server replies with:
```json
{ "type": "pong", "timestamp": 1729875615.42 }
```

---

## 4. Python Module API Reference

### 4.1 `OptimizedGestureModel` (`backend/models/model_runner.py`)
```python
from backend.models.model_runner import OptimizedGestureModel
import numpy as np

model = OptimizedGestureModel(model_path="backend/models/gesture_model.onnx")
roi = np.zeros((50, 50), dtype=np.uint8)
gesture_name, confidence = model.predict(roi)  # -> ('nothing', 0.95)
avg_latency_ms = model.benchmark(iterations=50)
```

### 4.2 `SkinDetector` & `GestureEngine` (`backend/engine.py`)
```python
from backend.engine import SkinDetector, GestureEngine

detector = SkinDetector(lower_cr=130, upper_cr=170, lower_cb=77, upper_cb=127)
hand_gray, binary_mask = detector.detect_with_mask(bgr_frame)

engine = GestureEngine(
    model_path="backend/models/gesture_model.onnx",
    confidence_threshold=0.70,
    smoothing_frames=20,
    fps_target=30,
)
engine.register_callback(lambda event_type, data: print(event_type, data))
engine.start()
status_dict = engine.get_status()
engine.stop()
```

### 4.3 `WindowsController` (`backend/controller.py`)
```python
from backend.controller import WindowsController

controller = WindowsController()
controller.execute_action("app_switch")   # Presses Alt+Tab
controller.execute_action("scroll_up")    # Scrolls +200 units
controller.execute_action("volume_up")    # Triggers Key.media_volume_up
```
