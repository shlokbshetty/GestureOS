# GestureOS — API & WebSocket Documentation

The GestureOS backend provides a high-performance REST API and WebSocket streaming interface powered by FastAPI.

- **Base URL**: `http://localhost:5000`
- **WebSocket Endpoint**: `ws://localhost:5000/ws`

---

## REST Endpoints

### 1. System Status
`GET /api/status`

Retrieves the current engine state, uptime, active gesture, and action counts.

#### Response:
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
  "uptime_seconds": 124.5,
  "total_actions": 18,
  "timestamp": 1729875600.15
}
```

---

### 2. Engine Lifecycle Controls

#### `POST /api/start`
Starts webcam frame capture and gesture inference.
- **Success (200)**: `{"success": true, "state": "running"}`
- **Conflict (409)**: Returned if engine is not in `stopped` state.

#### `POST /api/stop`
Stops gesture recognition and safely releases the camera device.
- **Success (200)**: `{"success": true, "state": "stopped"}`

#### `POST /api/pause`
Temporarily suspends gesture interception while keeping camera hardware initialized.
- **Success (200)**: `{"success": true, "state": "paused"}`

#### `POST /api/resume`
Resumes active gesture interception from `paused` state.
- **Success (200)**: `{"success": true, "state": "running"}`

---

### 3. Configuration Management

#### `GET /api/config`
Retrieves the complete application configuration including all gesture definitions and confidence parameters.

#### `POST /api/config`
Dynamically updates engine tuning parameters at runtime.

#### Request Body:
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

---

### 4. Gesture Registry

#### `GET /api/gestures`
Returns metadata dictionary for all 9 recognized gesture classes.

#### `PUT /api/gestures/{gesture_name}`
Updates keybinding, cooldown, or enabled status for a specific gesture.

#### Request Body:
```json
{
  "enabled": false,
  "cooldown_ms": 500
}
```

---

### 5. Action History & Telemetry

#### `GET /api/logs?limit=50`
Fetches recent executed actions in reverse chronological order.

#### `DELETE /api/logs`
Clears action history logs.

#### `GET /api/camera-status`
Returns camera connectivity, target FPS, and inference latency.
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

## WebSocket Telemetry Protocol (`/ws`)

Connect to `ws://localhost:5000/ws` for real-time push telemetry.

### Events Broadcast by Server:

#### 1. Connection Established
```json
{
  "type": "connection_established",
  "data": { ...statusObject... },
  "timestamp": 1729875600.0
}
```

#### 2. Gesture Detected
Emitted whenever a hand gesture is detected and passes temporal smoothing.
```json
{
  "type": "gesture_detected",
  "data": {
    "gesture": "volume_up",
    "confidence": 0.94,
    "timestamp": 1729875605.3
  },
  "timestamp": 1729875605.3
}
```

#### 3. State Changed
Emitted on lifecycle state machine transitions.
```json
{
  "type": "state_changed",
  "data": {
    "old_state": "stopped",
    "new_state": "running",
    "timestamp": 1729875601.0
  },
  "timestamp": 1729875601.0
}
```

#### 4. Action Executed
Emitted after Windows virtual keyboard/mouse operation completes.
```json
{
  "type": "action_executed",
  "data": {
    "gesture": "app_switch",
    "action": "keyboard_shortcut",
    "confidence": 0.91,
    "timestamp": 1729875610.1,
    "success": true
  },
  "timestamp": 1729875610.1
}
```

### Client Messages:
Clients can send heartbeat ping messages:
```json
{ "type": "ping" }
```
Server responds with:
```json
{ "type": "pong", "timestamp": 1729875611.0 }
```
