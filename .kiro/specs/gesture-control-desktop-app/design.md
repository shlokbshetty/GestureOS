# Gesture Control Desktop Application - Technical Design Document

## Overview

This document provides a comprehensive technical design for transforming the Gesture Control ACT project into a production-ready Windows desktop application with enhanced accessibility features, model training capabilities, and multi-language gesture support. The system architecture consists of four main layers:

1. **Backend Service (Python)**: Real-time gesture recognition engine with Windows automation, model management, and accessibility features
2. **Frontend Dashboard (React + TypeScript)**: Modern web-based UI with accessibility controls, high contrast support, and keyboard navigation
3. **Desktop Wrapper (Electron/Tauri)**: Native Windows application packaging with system integration
4. **Model Management System**: Support for multiple gesture vocabularies, model retraining, and versioning

The design emphasizes modularity, thread safety, real-time performance, graceful error handling, and inclusive accessibility for disabled users.

## System Architecture

### High-Level Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    DESKTOP WRAPPER (Electron/Tauri)             │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  System Tray Manager                                     │   │
│  │  - Start/Stop Controls                                   │   │
│  │  - Auto-start Configuration                              │   │
│  └──────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Backend Process Manager                                 │   │
│  │  - Launch Python service                                 │   │
│  │  - Monitor health                                        │   │
│  │  - Auto-restart on crash                                 │   │
│  └──────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Frontend Window Manager                                 │   │
│  │  - Embedded browser (React Dashboard)                    │   │
│  │  - Window lifecycle                                      │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ↕ (IPC)
┌─────────────────────────────────────────────────────────────────┐
│                    BACKEND SERVICE (Python)                      │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Gesture Engine (Vision Pipeline)                        │   │
│  │  - Camera capture (30 FPS)                               │   │
│  │  - Skin detection (YCrCb)                                │   │
│  │  - CNN inference                                         │   │
│  │  - Temporal smoothing                                    │   │
│  └──────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  State Manager                                           │   │
│  │  - Application lifecycle                                 │   │
│  │  - Gesture tracking                                      │   │
│  │  - Cooldown management                                   │   │
│  └──────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Windows Controller                                      │   │
│  │  - Keyboard automation                                   │   │
│  │  - Mouse control                                         │   │
│  │  - Media key handling                                    │   │
│  └──────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  API Server (FastAPI)                                    │   │
│  │  - REST endpoints                                        │   │
│  │  - WebSocket streaming                                   │   │
│  │  - Configuration management                              │   │
│  └──────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Gesture Registry                                        │   │
│  │  - Gesture-to-action mapping                             │   │
│  │  - Configuration persistence                             │   │
│  └──────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Utilities                                               │   │
│  │  - Logger (structured, file rotation)                    │   │
│  │  - Debounce/Cooldown system                              │   │
│  │  - Temporal smoothing                                    │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                    ↕ (REST API + WebSocket)
┌─────────────────────────────────────────────────────────────────┐
│                  FRONTEND DASHBOARD (React)                      │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  App (Root Component)                                    │   │
│  │  - WebSocket connection                                  │   │
│  │  - Global state management                               │   │
│  └──────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Dashboard Layout                                        │   │
│  │  - Controls Panel (Start/Stop/Pause)                     │   │
│  │  - Gesture Display (Real-time)                           │   │
│  │  - Camera Feed (Live preview)                            │   │
│  │  - Action Log (Recent actions)                           │   │
│  │  - Configuration Panel (Sliders, toggles)                │   │
│  │  - Statistics Panel (Metrics)                            │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow Diagram

```
CAMERA INPUT
    ↓
[Engine] Frame Capture (30 FPS)
    ↓
[Engine] Skin Detection (YCrCb)
    ↓
[Engine] Image Normalization (50x50, 0-1 range)
    ↓
[Engine] CNN Inference (TensorFlow)
    ↓
[Engine] Confidence Check (>70%)
    ↓
[Engine] Temporal Smoothing (20+ frames)
    ↓
gesture_detected event
    ↓
[State Manager] Cooldown Check
    ↓
[Controller] Execute Action (keyboard/mouse/media)
    ↓
[State Manager] Update state, log action
    ↓
[API Server] Broadcast via WebSocket
    ↓
[Dashboard] Update UI (gesture display, action log)
```



## Backend Design (Python)

### Module Structure

```
backend/
├── engine.py                 # Vision pipeline and gesture detection
├── controller.py             # Windows automation (keyboard, mouse, media)
├── gesture_registry.py       # Gesture-to-action mapping
├── state_manager.py          # Application lifecycle and state tracking
├── api_server.py             # FastAPI REST API and WebSocket
├── utils/
│   ├── logger.py             # Structured logging with rotation
│   ├── debounce.py           # Debounce and cooldown system
│   ├── smoothing.py          # Temporal smoothing algorithm
│   └── config.py             # Configuration management
├── models/
│   └── cnn_model_keras.h5    # Pre-trained CNN model
└── config.json               # Application configuration
```

### 1. engine.py - Vision Pipeline

**Responsibilities:**
- Camera capture and frame processing
- Skin detection using YCrCb color space
- CNN inference for gesture classification
- Temporal smoothing for stable predictions
- Event emission for detected gestures

**Key Classes:**

```python
class GestureEngine:
    """
    Core vision pipeline for real-time gesture recognition.
    
    Attributes:
        camera: OpenCV VideoCapture object
        model: Loaded TensorFlow/Keras CNN model
        frame_buffer: Deque tracking recent gesture predictions
        confidence_threshold: Minimum confidence for acceptance (default 70%)
        smoothing_frames: Frames required for gesture confirmation (default 20)
        running: Boolean flag for engine state
        fps_target: Target frames per second (30)
        inference_latency: Time in ms for CNN inference
    """
    
    def __init__(self, model_path: str, confidence_threshold: float = 0.70):
        """Initialize engine with model and parameters."""
        self.camera = None
        self.model = self._load_model(model_path)
        self.frame_buffer = deque(maxlen=30)  # Track last 30 predictions
        self.confidence_threshold = confidence_threshold
        self.smoothing_frames = 20
        self.running = False
        self.fps_target = 30
        self.inference_latency = 0
        self.skin_detector = SkinDetector()
        self.event_callbacks = []
        
    def start(self) -> bool:
        """
        Initialize camera and start processing thread.
        
        Returns:
            True if successful, False if camera unavailable
        """
        try:
            self.camera = cv2.VideoCapture(0)
            if not self.camera.isOpened():
                self.camera = cv2.VideoCapture(1)  # Try alternate camera
            
            if not self.camera.isOpened():
                self._emit_event('camera_error', {'message': 'No camera available'})
                return False
            
            self.running = True
            self.processing_thread = threading.Thread(target=self._process_loop)
            self.processing_thread.daemon = True
            self.processing_thread.start()
            return True
        except Exception as e:
            self._emit_event('camera_error', {'message': str(e)})
            return False
    
    def stop(self):
        """Stop processing and release camera."""
        self.running = False
        if self.processing_thread:
            self.processing_thread.join(timeout=5)
        if self.camera:
            self.camera.release()
    
    def _process_loop(self):
        """Main processing loop running at 30 FPS."""
        frame_time = 1000 / self.fps_target  # 33ms per frame
        
        while self.running:
            start_time = time.time()
            
            ret, frame = self.camera.read()
            if not ret:
                self._emit_event('camera_error', {'message': 'Failed to read frame'})
                continue
            
            # Process frame through pipeline
            gesture, confidence = self._process_frame(frame)
            
            # Apply temporal smoothing
            confirmed_gesture = self._apply_temporal_smoothing(gesture, confidence)
            
            if confirmed_gesture:
                self._emit_event('gesture_detected', {
                    'gesture': confirmed_gesture['gesture'],
                    'confidence': confirmed_gesture['confidence'],
                    'timestamp': time.time()
                })
            
            # Maintain target FPS
            elapsed = (time.time() - start_time) * 1000
            sleep_time = max(0, frame_time - elapsed)
            time.sleep(sleep_time / 1000)
    
    def _process_frame(self, frame: np.ndarray) -> tuple:
        """
        Process single frame through vision pipeline.
        
        Args:
            frame: OpenCV frame (BGR format)
        
        Returns:
            Tuple of (gesture_name, confidence_score)
        """
        start_time = time.time()
        
        # Step 1: Skin detection
        hand_region = self.skin_detector.detect(frame)
        if hand_region is None:
            return 'nothing', 0.0
        
        # Step 2: Normalize to model input size (50x50)
        normalized = cv2.resize(hand_region, (50, 50))
        normalized = normalized.astype('float32') / 255.0
        normalized = np.reshape(normalized, (1, 50, 50, 1))
        
        # Step 3: CNN inference
        predictions = self.model.predict(normalized, verbose=0)
        gesture_idx = np.argmax(predictions[0])
        confidence = float(predictions[0][gesture_idx])
        
        # Step 4: Confidence threshold check
        if confidence < self.confidence_threshold:
            return 'nothing', 0.0
        
        gesture_name = self._idx_to_gesture(gesture_idx)
        
        # Track inference latency
        self.inference_latency = (time.time() - start_time) * 1000
        
        return gesture_name, confidence
    
    def _apply_temporal_smoothing(self, gesture: str, confidence: float) -> dict:
        """
        Apply temporal smoothing to stabilize predictions.
        
        Algorithm:
        1. Add current prediction to frame buffer
        2. Count consecutive frames with same gesture
        3. If count >= smoothing_frames, confirm gesture
        4. If different gesture detected, reset buffer
        
        Args:
            gesture: Predicted gesture name
            confidence: Prediction confidence
        
        Returns:
            Dict with confirmed gesture or None
        """
        self.frame_buffer.append((gesture, confidence))
        
        if len(self.frame_buffer) < self.smoothing_frames:
            return None
        
        # Check if last N frames have same gesture
        recent_frames = list(self.frame_buffer)[-self.smoothing_frames:]
        gestures = [g for g, _ in recent_frames]
        
        if len(set(gestures)) == 1 and gestures[0] != 'nothing':
            # All recent frames have same gesture
            avg_confidence = np.mean([c for _, c in recent_frames])
            self.frame_buffer.clear()  # Reset buffer after confirmation
            return {
                'gesture': gestures[0],
                'confidence': avg_confidence
            }
        
        return None
    
    def _emit_event(self, event_type: str, data: dict):
        """Emit event to registered callbacks."""
        for callback in self.event_callbacks:
            callback(event_type, data)
    
    def register_callback(self, callback):
        """Register callback for engine events."""
        self.event_callbacks.append(callback)
```

**Skin Detection Algorithm (YCrCb):**

```python
class SkinDetector:
    """
    Detect hand region using YCrCb color space.
    
    YCrCb is more robust to lighting changes than RGB.
    Skin pixels typically have:
    - Cr: 130-170
    - Cb: 77-127
    """
    
    def detect(self, frame: np.ndarray) -> np.ndarray:
        """
        Detect hand region in frame.
        
        Args:
            frame: OpenCV frame (BGR)
        
        Returns:
            Isolated hand region or None if not found
        """
        # Convert BGR to YCrCb
        ycrcb = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb)
        
        # Define skin color range in YCrCb
        lower_skin = np.array([0, 130, 77])
        upper_skin = np.array([255, 170, 127])
        
        # Create mask
        mask = cv2.inRange(ycrcb, lower_skin, upper_skin)
        
        # Morphological operations to clean mask
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        
        # Find largest contour (hand)
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return None
        
        largest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour)
        
        # Extract hand region with padding
        padding = 10
        x = max(0, x - padding)
        y = max(0, y - padding)
        w = min(frame.shape[1] - x, w + 2 * padding)
        h = min(frame.shape[0] - y, h + 2 * padding)
        
        hand_region = frame[y:y+h, x:x+w]
        
        # Convert to grayscale for model input
        hand_region = cv2.cvtColor(hand_region, cv2.COLOR_BGR2GRAY)
        
        return hand_region if hand_region.size > 0 else None
```



### 2. controller.py - Windows Automation

**Responsibilities:**
- Execute keyboard shortcuts
- Control mouse movement and scrolling
- Handle media keys
- Log action execution
- Handle execution failures

**Key Classes:**

```python
class WindowsController:
    """
    Execute system actions on Windows via keyboard/mouse/media keys.
    
    Uses pyautogui for cross-platform compatibility and pynput for media keys.
    """
    
    def __init__(self, logger):
        self.logger = logger
        self.action_callbacks = []
    
    def execute_action(self, action_type: str, params: dict = None) -> bool:
        """
        Execute system action.
        
        Args:
            action_type: Type of action (keyboard, mouse, media)
            params: Action parameters
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if action_type == 'app_switch':
                self._keyboard_shortcut(['alt', 'tab'])
            elif action_type == 'close_window':
                self._keyboard_shortcut(['alt', 'F4'])
            elif action_type == 'play_pause':
                self._keyboard_key('space')
            elif action_type == 'volume_up':
                self._media_key('volume_up')
            elif action_type == 'volume_down':
                self._media_key('volume_down')
            elif action_type == 'scroll_up':
                self._mouse_scroll(200)
            elif action_type == 'scroll_down':
                self._mouse_scroll(-200)
            elif action_type == 'screenshot':
                self._keyboard_key('print')
            else:
                self.logger.warning(f'Unknown action type: {action_type}')
                return False
            
            self.logger.info(f'Action executed: {action_type}')
            self._emit_callback('action_executed', {'action': action_type})
            return True
        
        except Exception as e:
            self.logger.error(f'Action execution failed: {action_type}, {str(e)}')
            self._emit_callback('action_failed', {'action': action_type, 'error': str(e)})
            return False
    
    def _keyboard_shortcut(self, keys: list):
        """Execute keyboard shortcut (e.g., Alt+Tab)."""
        keyboard = Controller()
        for key in keys[:-1]:
            keyboard.press(Key[key.lower()])
        
        keyboard.press(Key[keys[-1].lower()] if keys[-1].lower() in Key.__dict__ else keys[-1])
        
        for key in reversed(keys):
            keyboard.release(Key[key.lower()] if key.lower() in Key.__dict__ else key)
    
    def _keyboard_key(self, key: str):
        """Press single keyboard key."""
        keyboard = Controller()
        keyboard.press(Key[key.lower()] if key.lower() in Key.__dict__ else key)
        keyboard.release(Key[key.lower()] if key.lower() in Key.__dict__ else key)
    
    def _media_key(self, key: str):
        """Execute media key (volume, play, etc.)."""
        keyboard = Controller()
        if key == 'volume_up':
            keyboard.press(Key.media_volume_up)
            keyboard.release(Key.media_volume_up)
        elif key == 'volume_down':
            keyboard.press(Key.media_volume_down)
            keyboard.release(Key.media_volume_down)
        elif key == 'play_pause':
            keyboard.press(Key.media_play_pause)
            keyboard.release(Key.media_play_pause)
    
    def _mouse_scroll(self, units: int):
        """Scroll mouse wheel."""
        mouse = Mouse()
        mouse.scroll(0, units)
    
    def register_callback(self, callback):
        """Register callback for action events."""
        self.action_callbacks.append(callback)
    
    def _emit_callback(self, event_type: str, data: dict):
        """Emit event to registered callbacks."""
        for callback in self.action_callbacks:
            callback(event_type, data)
```

### 3. gesture_registry.py - Gesture Mapping

**Responsibilities:**
- Maintain gesture-to-action mappings
- Load/save configuration
- Provide gesture metadata
- Support enable/disable per gesture

**Key Classes:**

```python
class GestureRegistry:
    """
    Central registry for gesture-to-action mappings.
    
    Loads from config.json and supports runtime updates.
    """
    
    DEFAULT_GESTURES = {
        'app_switch': {
            'action': 'keyboard_shortcut',
            'params': {'keys': ['alt', 'tab']},
            'cooldown_ms': 500,
            'enabled': True,
            'display_name': 'App Switch',
            'icon': 'app_switch.svg',
            'description': 'Switch between open applications'
        },
        'close_window': {
            'action': 'keyboard_shortcut',
            'params': {'keys': ['alt', 'F4']},
            'cooldown_ms': 500,
            'enabled': True,
            'display_name': 'Close Window',
            'icon': 'close_window.svg',
            'description': 'Close current window'
        },
        'play_pause': {
            'action': 'keyboard_key',
            'params': {'key': 'space'},
            'cooldown_ms': 300,
            'enabled': True,
            'display_name': 'Play/Pause',
            'icon': 'play_pause.svg',
            'description': 'Play or pause media'
        },
        'volume_up': {
            'action': 'media_key',
            'params': {'key': 'volume_up'},
            'cooldown_ms': 200,
            'enabled': True,
            'display_name': 'Volume Up',
            'icon': 'volume_up.svg',
            'description': 'Increase volume'
        },
        'volume_down': {
            'action': 'media_key',
            'params': {'key': 'volume_down'},
            'cooldown_ms': 200,
            'enabled': True,
            'display_name': 'Volume Down',
            'icon': 'volume_down.svg',
            'description': 'Decrease volume'
        },
        'scroll_up': {
            'action': 'mouse_scroll',
            'params': {'units': 200},
            'cooldown_ms': 100,
            'enabled': True,
            'display_name': 'Scroll Up',
            'icon': 'scroll_up.svg',
            'description': 'Scroll up'
        },
        'scroll_down': {
            'action': 'mouse_scroll',
            'params': {'units': -200},
            'cooldown_ms': 100,
            'enabled': True,
            'display_name': 'Scroll Down',
            'icon': 'scroll_down.svg',
            'description': 'Scroll down'
        },
        'screenshot': {
            'action': 'keyboard_key',
            'params': {'key': 'print'},
            'cooldown_ms': 1000,
            'enabled': True,
            'display_name': 'Screenshot',
            'icon': 'screenshot.svg',
            'description': 'Take screenshot'
        },
        'nothing': {
            'action': 'none',
            'params': {},
            'cooldown_ms': 0,
            'enabled': True,
            'display_name': 'No Gesture',
            'icon': 'nothing.svg',
            'description': 'No gesture detected'
        }
    }
    
    def __init__(self, config_path: str = 'config.json'):
        self.config_path = config_path
        self.gestures = self._load_config()
    
    def _load_config(self) -> dict:
        """Load gesture configuration from file."""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
                return config.get('gestures', self.DEFAULT_GESTURES)
        except FileNotFoundError:
            return self.DEFAULT_GESTURES.copy()
    
    def save_config(self):
        """Persist gesture configuration to file."""
        config = {'gestures': self.gestures}
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)
    
    def get_action(self, gesture_name: str) -> dict:
        """
        Get action for gesture.
        
        Returns:
            Dict with action type, params, cooldown, or None if disabled
        """
        if gesture_name not in self.gestures:
            return None
        
        gesture = self.gestures[gesture_name]
        if not gesture.get('enabled', True):
            return None
        
        return {
            'action': gesture['action'],
            'params': gesture['params'],
            'cooldown_ms': gesture['cooldown_ms']
        }
    
    def update_gesture(self, gesture_name: str, updates: dict):
        """Update gesture configuration."""
        if gesture_name in self.gestures:
            self.gestures[gesture_name].update(updates)
            self.save_config()
    
    def get_all_gestures(self) -> dict:
        """Get all gesture metadata."""
        return self.gestures
    
    def set_enabled(self, gesture_name: str, enabled: bool):
        """Enable or disable gesture."""
        if gesture_name in self.gestures:
            self.gestures[gesture_name]['enabled'] = enabled
            self.save_config()
```



### 4. state_manager.py - Application Lifecycle

**Responsibilities:**
- Manage application state machine
- Track current gesture and last action
- Manage cooldown periods
- Emit state change events
- Handle graceful shutdown

**Key Classes:**

```python
class StateManager:
    """
    Manage application lifecycle and state transitions.
    
    State Machine:
        stopped -> starting -> running
                              ↓
                            pausing -> paused
                              ↑
                            resuming
                              ↓
                            stopping -> stopped
    """
    
    STATES = {
        'stopped': 0,
        'starting': 1,
        'running': 2,
        'pausing': 3,
        'paused': 4,
        'stopping': 5
    }
    
    def __init__(self, engine, controller, registry, logger):
        self.engine = engine
        self.controller = controller
        self.registry = registry
        self.logger = logger
        
        self.state = 'stopped'
        self.current_gesture = 'nothing'
        self.last_action = None
        self.last_action_time = 0
        self.start_time = None
        self.action_log = deque(maxlen=1000)
        self.state_callbacks = []
        self.cooldown_tracker = {}  # gesture -> expiry_time
        self.lock = threading.RLock()
    
    def start(self) -> bool:
        """Start gesture recognition."""
        with self.lock:
            if self.state != 'stopped':
                self.logger.warning(f'Cannot start from state: {self.state}')
                return False
            
            self._transition_state('starting')
            
            if not self.engine.start():
                self._transition_state('stopped')
                return False
            
            self.start_time = time.time()
            self._transition_state('running')
            self.logger.info('Application started')
            return True
    
    def stop(self) -> bool:
        """Stop gesture recognition."""
        with self.lock:
            if self.state == 'stopped':
                return True
            
            self._transition_state('stopping')
            
            # Wait for in-flight actions (max 5 seconds)
            timeout = time.time() + 5
            while self.last_action_time > time.time() - 1 and time.time() < timeout:
                time.sleep(0.1)
            
            self.engine.stop()
            self._transition_state('stopped')
            self.logger.info('Application stopped')
            return True
    
    def pause(self) -> bool:
        """Pause gesture detection."""
        with self.lock:
            if self.state != 'running':
                return False
            
            self._transition_state('pausing')
            self.engine.running = False
            self._transition_state('paused')
            self.logger.info('Application paused')
            return True
    
    def resume(self) -> bool:
        """Resume gesture detection."""
        with self.lock:
            if self.state != 'paused':
                return False
            
            self._transition_state('running')
            self.engine.running = True
            self.logger.info('Application resumed')
            return True
    
    def on_gesture_detected(self, gesture: str, confidence: float):
        """Handle gesture detection event."""
        with self.lock:
            if self.state != 'running':
                return
            
            self.current_gesture = gesture
            
            # Check cooldown
            if not self._check_cooldown(gesture):
                self.logger.debug(f'Gesture {gesture} in cooldown')
                return
            
            # Get action from registry
            action_info = self.registry.get_action(gesture)
            if not action_info:
                return
            
            # Execute action
            success = self.controller.execute_action(
                action_info['action'],
                action_info['params']
            )
            
            if success:
                self.last_action = gesture
                self.last_action_time = time.time()
                
                # Set cooldown
                cooldown_ms = action_info['cooldown_ms']
                self.cooldown_tracker[gesture] = time.time() + (cooldown_ms / 1000)
                
                # Log action
                self.action_log.append({
                    'gesture': gesture,
                    'action': action_info['action'],
                    'confidence': confidence,
                    'timestamp': time.time(),
                    'success': True
                })
                
                self.logger.info(f'Action executed: {gesture} ({confidence:.2%})')
    
    def _check_cooldown(self, gesture: str) -> bool:
        """Check if gesture is in cooldown period."""
        if gesture not in self.cooldown_tracker:
            return True
        
        expiry = self.cooldown_tracker[gesture]
        if time.time() >= expiry:
            del self.cooldown_tracker[gesture]
            return True
        
        return False
    
    def _transition_state(self, new_state: str):
        """Transition to new state and emit event."""
        old_state = self.state
        self.state = new_state
        self.logger.info(f'State transition: {old_state} -> {new_state}')
        self._emit_callback('state_changed', {
            'old_state': old_state,
            'new_state': new_state,
            'timestamp': time.time()
        })
    
    def get_status(self) -> dict:
        """Get current application status."""
        with self.lock:
            uptime = time.time() - self.start_time if self.start_time else 0
            return {
                'state': self.state,
                'current_gesture': self.current_gesture,
                'last_action': self.last_action,
                'uptime': uptime,
                'total_actions': len(self.action_log),
                'inference_latency': self.engine.inference_latency
            }
    
    def get_action_log(self, limit: int = 100) -> list:
        """Get recent action log entries."""
        with self.lock:
            return list(self.action_log)[-limit:]
    
    def register_callback(self, callback):
        """Register callback for state events."""
        self.state_callbacks.append(callback)
    
    def _emit_callback(self, event_type: str, data: dict):
        """Emit event to registered callbacks."""
        for callback in self.state_callbacks:
            callback(event_type, data)
```

### 5. api_server.py - REST API and WebSocket

**Responsibilities:**
- Provide REST endpoints for control and monitoring
- Stream real-time events via WebSocket
- Handle configuration updates
- Serve action logs

**Key Classes:**

```python
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import asyncio

class APIServer:
    """
    FastAPI server providing REST API and WebSocket streaming.
    
    Endpoints:
        GET  /api/status           - Application status
        POST /api/start            - Start engine
        POST /api/stop             - Stop engine
        POST /api/pause            - Pause detection
        POST /api/resume           - Resume detection
        GET  /api/config           - Get configuration
        POST /api/config           - Update configuration
        GET  /api/logs             - Get action logs
        GET  /api/camera-status    - Camera status
        WS   /ws                   - WebSocket stream
    """
    
    def __init__(self, state_manager, engine, registry, logger, port: int = 5000):
        self.state_manager = state_manager
        self.engine = engine
        self.registry = registry
        self.logger = logger
        self.port = port
        
        self.app = FastAPI()
        self.websocket_clients = set()
        self.setup_routes()
        self.setup_middleware()
    
    def setup_middleware(self):
        """Configure CORS and other middleware."""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=['localhost', '127.0.0.1'],
            allow_credentials=True,
            allow_methods=['*'],
            allow_headers=['*']
        )
    
    def setup_routes(self):
        """Setup API routes."""
        
        @self.app.get('/api/status')
        async def get_status():
            return self.state_manager.get_status()
        
        @self.app.post('/api/start')
        async def start():
            success = self.state_manager.start()
            return {'success': success, 'state': self.state_manager.state}
        
        @self.app.post('/api/stop')
        async def stop():
            success = self.state_manager.stop()
            return {'success': success, 'state': self.state_manager.state}
        
        @self.app.post('/api/pause')
        async def pause():
            success = self.state_manager.pause()
            return {'success': success, 'state': self.state_manager.state}
        
        @self.app.post('/api/resume')
        async def resume():
            success = self.state_manager.resume()
            return {'success': success, 'state': self.state_manager.state}
        
        @self.app.get('/api/config')
        async def get_config():
            return {
                'gestures': self.registry.get_all_gestures(),
                'confidence_threshold': self.engine.confidence_threshold,
                'smoothing_frames': self.engine.smoothing_frames
            }
        
        @self.app.post('/api/config')
        async def update_config(config: dict):
            try:
                if 'confidence_threshold' in config:
                    self.engine.confidence_threshold = config['confidence_threshold']
                if 'smoothing_frames' in config:
                    self.engine.smoothing_frames = config['smoothing_frames']
                if 'gestures' in config:
                    for gesture_name, updates in config['gestures'].items():
                        self.registry.update_gesture(gesture_name, updates)
                
                await self.broadcast_event('config_updated', config)
                return {'success': True}
            except Exception as e:
                self.logger.error(f'Config update failed: {str(e)}')
                return {'success': False, 'error': str(e)}
        
        @self.app.get('/api/logs')
        async def get_logs(limit: int = 100):
            return {'logs': self.state_manager.get_action_log(limit)}
        
        @self.app.get('/api/camera-status')
        async def get_camera_status():
            return {
                'connected': self.engine.camera is not None and self.engine.camera.isOpened(),
                'fps': self.engine.fps_target,
                'inference_latency_ms': self.engine.inference_latency
            }
        
        @self.app.websocket('/ws')
        async def websocket_endpoint(websocket: WebSocket):
            await websocket.accept()
            self.websocket_clients.add(websocket)
            
            try:
                while True:
                    # Keep connection alive
                    await asyncio.sleep(1)
            except Exception as e:
                self.logger.error(f'WebSocket error: {str(e)}')
            finally:
                self.websocket_clients.discard(websocket)
    
    async def broadcast_event(self, event_type: str, data: dict):
        """Broadcast event to all connected WebSocket clients."""
        message = {
            'type': event_type,
            'data': data,
            'timestamp': time.time()
        }
        
        disconnected = set()
        for client in self.websocket_clients:
            try:
                await client.send_json(message)
            except Exception as e:
                self.logger.debug(f'Failed to send to client: {str(e)}')
                disconnected.add(client)
        
        self.websocket_clients -= disconnected
    
    def run(self):
        """Start API server."""
        import uvicorn
        self.logger.info(f'Starting API server on localhost:{self.port}')
        uvicorn.run(self.app, host='127.0.0.1', port=self.port, log_level='info')
```



### 6. Utility Modules

#### utils/logger.py - Structured Logging

```python
import logging
from logging.handlers import RotatingFileHandler

class StructuredLogger:
    """
    Structured logging with file rotation.
    
    Features:
    - Timestamps and severity levels
    - Component names
    - File rotation (10MB max, 5 files kept)
    - Console and file output
    """
    
    def __init__(self, name: str, log_file: str = 'logs/app.log'):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # File handler with rotation
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def debug(self, msg: str):
        self.logger.debug(msg)
    
    def info(self, msg: str):
        self.logger.info(msg)
    
    def warning(self, msg: str):
        self.logger.warning(msg)
    
    def error(self, msg: str):
        self.logger.error(msg)
    
    def critical(self, msg: str):
        self.logger.critical(msg)
```

#### utils/debounce.py - Debounce and Cooldown

```python
import time
from typing import Callable

class Debouncer:
    """
    Debounce rapid events within a time window.
    
    Algorithm:
    1. Track last event time
    2. If new event within window, ignore it
    3. If outside window, process event
    """
    
    def __init__(self, window_ms: int = 500):
        self.window_ms = window_ms
        self.last_event_time = 0
    
    def should_process(self) -> bool:
        """Check if event should be processed."""
        now = time.time() * 1000
        if now - self.last_event_time >= self.window_ms:
            self.last_event_time = now
            return True
        return False
    
    def reset(self):
        """Reset debounce timer."""
        self.last_event_time = 0


class CooldownTracker:
    """
    Track cooldown periods for multiple gestures.
    
    Prevents rapid re-triggering of same gesture.
    """
    
    def __init__(self):
        self.cooldowns = {}  # gesture -> expiry_time
    
    def set_cooldown(self, gesture: str, duration_ms: int):
        """Set cooldown for gesture."""
        self.cooldowns[gesture] = time.time() + (duration_ms / 1000)
    
    def is_in_cooldown(self, gesture: str) -> bool:
        """Check if gesture is in cooldown."""
        if gesture not in self.cooldowns:
            return False
        
        if time.time() >= self.cooldowns[gesture]:
            del self.cooldowns[gesture]
            return False
        
        return True
    
    def get_remaining_ms(self, gesture: str) -> int:
        """Get remaining cooldown time in ms."""
        if gesture not in self.cooldowns:
            return 0
        
        remaining = self.cooldowns[gesture] - time.time()
        return max(0, int(remaining * 1000))
```

#### utils/smoothing.py - Temporal Smoothing

```python
from collections import deque
import numpy as np

class TemporalSmoother:
    """
    Smooth predictions across multiple frames.
    
    Algorithm:
    1. Maintain buffer of recent predictions
    2. Count consecutive frames with same gesture
    3. Confirm gesture when threshold reached
    4. Reset on different gesture
    
    This prevents false positives from brief hand movements.
    """
    
    def __init__(self, smoothing_frames: int = 20):
        self.smoothing_frames = smoothing_frames
        self.frame_buffer = deque(maxlen=smoothing_frames)
    
    def add_prediction(self, gesture: str, confidence: float) -> dict:
        """
        Add prediction and check if confirmed.
        
        Args:
            gesture: Predicted gesture name
            confidence: Prediction confidence (0-1)
        
        Returns:
            Dict with confirmed gesture or None
        """
        self.frame_buffer.append((gesture, confidence))
        
        if len(self.frame_buffer) < self.smoothing_frames:
            return None
        
        # Check if all recent frames have same gesture
        gestures = [g for g, _ in self.frame_buffer]
        
        if len(set(gestures)) == 1 and gestures[0] != 'nothing':
            # All frames have same gesture
            avg_confidence = np.mean([c for _, c in self.frame_buffer])
            self.frame_buffer.clear()
            
            return {
                'gesture': gestures[0],
                'confidence': avg_confidence,
                'frames': self.smoothing_frames
            }
        
        return None
    
    def reset(self):
        """Clear buffer."""
        self.frame_buffer.clear()
    
    def get_buffer_state(self) -> dict:
        """Get current buffer state for debugging."""
        if not self.frame_buffer:
            return {'empty': True}
        
        gestures = [g for g, _ in self.frame_buffer]
        return {
            'size': len(self.frame_buffer),
            'recent_gesture': gestures[-1] if gestures else None,
            'unique_gestures': len(set(gestures)),
            'confidence_avg': np.mean([c for _, c in self.frame_buffer])
        }
```



## Frontend Design (React + TypeScript + Tailwind)

### Component Hierarchy

```
App (Root)
├── WebSocketProvider
│   └── Dashboard
│       ├── Header
│       │   ├── Logo
│       │   └── Status Indicator
│       ├── ControlPanel
│       │   ├── StartStopButton
│       │   ├── PauseResumeButton
│       │   └── StatusDisplay
│       ├── GestureDisplay
│       │   ├── CurrentGesture
│       │   └── ConfidenceBar
│       ├── CameraFeed
│       │   └── LivePreview
│       ├── ActionLog
│       │   └── LogEntry (repeated)
│       ├── ConfigPanel
│       │   ├── ConfidenceSlider
│       │   ├── CooldownSlider
│       │   └── GestureToggles
│       └── StatisticsPanel
│           ├── Uptime
│           ├── TotalGestures
│           ├── TotalActions
│           └── AvgLatency
```

### Design System (Neo-style)

**Color Palette:**
- Background: `#0a0e27` (deep navy)
- Surface: `#1a1f3a` (dark blue)
- Accent: `#00d9ff` (cyan)
- Success: `#00ff88` (neon green)
- Warning: `#ffaa00` (neon orange)
- Error: `#ff0055` (neon pink)
- Text: `#e0e0e0` (light gray)

**Typography:**
- Font: 'Inter', 'Roboto Mono' for code
- Headings: Bold, 24-32px
- Body: Regular, 14-16px
- Code: Monospace, 12-14px

**Effects:**
- Glassmorphism: `backdrop-filter: blur(10px)`, `background: rgba(255,255,255,0.05)`
- Sharp edges: No border-radius on main elements
- Glow effects: `box-shadow: 0 0 20px rgba(0, 217, 255, 0.3)`
- Transitions: 200ms ease-in-out

### Key Components

#### App.tsx - Root Component

```typescript
import React, { useEffect, useState } from 'react';
import { WebSocketProvider } from './context/WebSocketContext';
import Dashboard from './pages/Dashboard';
import './styles/globals.css';

export const App: React.FC = () => {
  const [isConnected, setIsConnected] = useState(false);

  return (
    <WebSocketProvider onConnect={() => setIsConnected(true)}>
      <div className="min-h-screen bg-gradient-to-br from-[#0a0e27] to-[#1a1f3a]">
        {!isConnected && (
          <div className="fixed inset-0 flex items-center justify-center bg-black/50 backdrop-blur-sm">
            <div className="text-center">
              <div className="animate-spin mb-4">
                <div className="w-12 h-12 border-2 border-[#00d9ff] border-t-transparent rounded-full" />
              </div>
              <p className="text-[#00d9ff] font-mono">Connecting to backend...</p>
            </div>
          </div>
        )}
        <Dashboard />
      </div>
    </WebSocketProvider>
  );
};

export default App;
```

#### Dashboard.tsx - Main Layout

```typescript
import React, { useState } from 'react';
import { useWebSocket } from '../context/WebSocketContext';
import ControlPanel from '../components/ControlPanel';
import GestureDisplay from '../components/GestureDisplay';
import CameraFeed from '../components/CameraFeed';
import ActionLog from '../components/ActionLog';
import ConfigPanel from '../components/ConfigPanel';
import StatisticsPanel from '../components/StatisticsPanel';

interface DashboardState {
  state: string;
  current_gesture: string;
  last_action: string | null;
  uptime: number;
  total_actions: number;
  inference_latency: number;
}

export const Dashboard: React.FC = () => {
  const { status, sendMessage } = useWebSocket();
  const [dashboardState, setDashboardState] = useState<DashboardState>({
    state: 'stopped',
    current_gesture: 'nothing',
    last_action: null,
    uptime: 0,
    total_actions: 0,
    inference_latency: 0
  });

  React.useEffect(() => {
    if (status) {
      setDashboardState(status);
    }
  }, [status]);

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-4xl font-bold text-[#00d9ff] font-mono">
            GESTURE CONTROL
          </h1>
          <p className="text-[#00ff88] text-sm mt-1">Real-time Hand Gesture Recognition</p>
        </div>
        <div className={`px-4 py-2 rounded-none border border-2 ${
          dashboardState.state === 'running' 
            ? 'border-[#00ff88] bg-[#00ff88]/10' 
            : 'border-[#ffaa00] bg-[#ffaa00]/10'
        }`}>
          <p className="text-sm font-mono uppercase">
            {dashboardState.state}
          </p>
        </div>
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-3 gap-6">
        {/* Left Column */}
        <div className="col-span-1 space-y-6">
          <ControlPanel state={dashboardState.state} onSendMessage={sendMessage} />
          <GestureDisplay gesture={dashboardState.current_gesture} />
          <StatisticsPanel state={dashboardState} />
        </div>

        {/* Center Column */}
        <div className="col-span-1">
          <CameraFeed />
        </div>

        {/* Right Column */}
        <div className="col-span-1 space-y-6">
          <ConfigPanel onSendMessage={sendMessage} />
          <ActionLog />
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
```

#### ControlPanel.tsx - Start/Stop/Pause Controls

```typescript
import React from 'react';

interface ControlPanelProps {
  state: string;
  onSendMessage: (message: any) => void;
}

export const ControlPanel: React.FC<ControlPanelProps> = ({ state, onSendMessage }) => {
  const handleStart = () => {
    onSendMessage({ type: 'start' });
  };

  const handleStop = () => {
    onSendMessage({ type: 'stop' });
  };

  const handlePause = () => {
    onSendMessage({ type: 'pause' });
  };

  const handleResume = () => {
    onSendMessage({ type: 'resume' });
  };

  return (
    <div className="bg-[#1a1f3a]/80 backdrop-blur-md border border-[#00d9ff]/20 p-6 space-y-4">
      <h2 className="text-xl font-bold text-[#00d9ff] font-mono">CONTROLS</h2>
      
      <div className="space-y-3">
        {state === 'stopped' ? (
          <button
            onClick={handleStart}
            className="w-full py-3 bg-[#00ff88] text-black font-bold uppercase tracking-wider hover:bg-[#00ff88]/80 transition-all"
          >
            ▶ START
          </button>
        ) : (
          <button
            onClick={handleStop}
            className="w-full py-3 bg-[#ff0055] text-white font-bold uppercase tracking-wider hover:bg-[#ff0055]/80 transition-all"
          >
            ⏹ STOP
          </button>
        )}

        {state === 'running' && (
          <button
            onClick={handlePause}
            className="w-full py-3 bg-[#ffaa00] text-black font-bold uppercase tracking-wider hover:bg-[#ffaa00]/80 transition-all"
          >
            ⏸ PAUSE
          </button>
        )}

        {state === 'paused' && (
          <button
            onClick={handleResume}
            className="w-full py-3 bg-[#00d9ff] text-black font-bold uppercase tracking-wider hover:bg-[#00d9ff]/80 transition-all"
          >
            ▶ RESUME
          </button>
        )}
      </div>
    </div>
  );
};

export default ControlPanel;
```

#### GestureDisplay.tsx - Real-time Gesture

```typescript
import React from 'react';

interface GestureDisplayProps {
  gesture: string;
}

export const GestureDisplay: React.FC<GestureDisplayProps> = ({ gesture }) => {
  const gestureIcons: Record<string, string> = {
    'app_switch': '🔄',
    'close_window': '❌',
    'play_pause': '⏯️',
    'volume_up': '🔊',
    'volume_down': '🔉',
    'scroll_up': '⬆️',
    'scroll_down': '⬇️',
    'screenshot': '📸',
    'nothing': '✋'
  };

  return (
    <div className="bg-[#1a1f3a]/80 backdrop-blur-md border border-[#00d9ff]/20 p-6 text-center">
      <h3 className="text-sm font-mono text-[#00d9ff] mb-4">CURRENT GESTURE</h3>
      <div className="text-6xl mb-4">{gestureIcons[gesture] || '✋'}</div>
      <p className="text-2xl font-bold text-[#00ff88] uppercase font-mono">
        {gesture.replace('_', ' ')}
      </p>
    </div>
  );
};

export default GestureDisplay;
```

#### WebSocketContext.tsx - Real-time Communication

```typescript
import React, { createContext, useContext, useEffect, useState } from 'react';

interface WebSocketContextType {
  status: any;
  sendMessage: (message: any) => void;
  isConnected: boolean;
}

const WebSocketContext = createContext<WebSocketContextType | undefined>(undefined);

interface WebSocketProviderProps {
  children: React.ReactNode;
  onConnect?: () => void;
}

export const WebSocketProvider: React.FC<WebSocketProviderProps> = ({ children, onConnect }) => {
  const [status, setStatus] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [ws, setWs] = useState<WebSocket | null>(null);

  useEffect(() => {
    const connectWebSocket = () => {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${protocol}//localhost:5000/ws`;

      const websocket = new WebSocket(wsUrl);

      websocket.onopen = () => {
        console.log('WebSocket connected');
        setIsConnected(true);
        onConnect?.();
      };

      websocket.onmessage = (event) => {
        const message = JSON.parse(event.data);
        
        if (message.type === 'status_update') {
          setStatus(message.data);
        } else if (message.type === 'gesture_detected') {
          // Update gesture display
          setStatus(prev => ({
            ...prev,
            current_gesture: message.data.gesture
          }));
        }
      };

      websocket.onerror = (error) => {
        console.error('WebSocket error:', error);
        setIsConnected(false);
      };

      websocket.onclose = () => {
        console.log('WebSocket disconnected');
        setIsConnected(false);
        // Attempt reconnection after 3 seconds
        setTimeout(connectWebSocket, 3000);
      };

      setWs(websocket);
    };

    connectWebSocket();

    return () => {
      ws?.close();
    };
  }, []);

  const sendMessage = (message: any) => {
    if (ws && isConnected) {
      ws.send(JSON.stringify(message));
    }
  };

  return (
    <WebSocketContext.Provider value={{ status, sendMessage, isConnected }}>
      {children}
    </WebSocketContext.Provider>
  );
};

export const useWebSocket = () => {
  const context = useContext(WebSocketContext);
  if (!context) {
    throw new Error('useWebSocket must be used within WebSocketProvider');
  }
  return context;
};
```



## Desktop Wrapper Design (Electron/Tauri)

### Architecture Overview

The desktop wrapper serves three main functions:
1. **Process Management**: Launch and monitor the Python backend service
2. **Window Management**: Host the React dashboard in an embedded browser
3. **System Integration**: System tray icon, auto-start, native notifications

### Electron Implementation (Recommended)

```typescript
// main.ts - Main process
import { app, BrowserWindow, Menu, Tray, ipcMain } from 'electron';
import { spawn, ChildProcess } from 'child_process';
import path from 'path';
import isDev from 'electron-is-dev';

class GestureControlApp {
  private mainWindow: BrowserWindow | null = null;
  private tray: Tray | null = null;
  private backendProcess: ChildProcess | null = null;
  private backendReady = false;

  constructor() {
    this.setupIPC();
    this.startBackendService();
  }

  private startBackendService() {
    /**
     * Start Python backend service.
     * 
     * In development: Run from source
     * In production: Run from bundled executable
     */
    const backendPath = isDev
      ? path.join(__dirname, '../backend/main.py')
      : path.join(process.resourcesPath, 'backend/main.exe');

    this.backendProcess = spawn('python', [backendPath], {
      stdio: 'pipe',
      detached: false
    });

    this.backendProcess.stdout?.on('data', (data) => {
      console.log(`Backend: ${data}`);
      if (data.toString().includes('API server started')) {
        this.backendReady = true;
        this.createWindow();
      }
    });

    this.backendProcess.stderr?.on('data', (data) => {
      console.error(`Backend error: ${data}`);
    });

    this.backendProcess.on('exit', (code) => {
      console.log(`Backend exited with code ${code}`);
      this.backendReady = false;
      // Attempt restart
      setTimeout(() => this.startBackendService(), 3000);
    });
  }

  private createWindow() {
    this.mainWindow = new BrowserWindow({
      width: 1920,
      height: 1080,
      minWidth: 1280,
      minHeight: 720,
      webPreferences: {
        preload: path.join(__dirname, 'preload.ts'),
        nodeIntegration: false,
        contextIsolation: true
      }
    });

    const startUrl = isDev
      ? 'http://localhost:3000'
      : `file://${path.join(__dirname, '../build/index.html')}`;

    this.mainWindow.loadURL(startUrl);

    this.mainWindow.on('closed', () => {
      this.mainWindow = null;
    });

    this.mainWindow.on('close', (event) => {
      event.preventDefault();
      this.showExitDialog();
    });

    if (isDev) {
      this.mainWindow.webContents.openDevTools();
    }
  }

  private setupTray() {
    const trayIcon = path.join(__dirname, '../assets/tray-icon.png');
    this.tray = new Tray(trayIcon);

    const contextMenu = Menu.buildFromTemplate([
      {
        label: 'Show Dashboard',
        click: () => {
          if (this.mainWindow) {
            this.mainWindow.show();
          }
        }
      },
      {
        label: 'Start Gesture Recognition',
        click: () => {
          this.mainWindow?.webContents.send('start-gesture-recognition');
        }
      },
      {
        label: 'Stop Gesture Recognition',
        click: () => {
          this.mainWindow?.webContents.send('stop-gesture-recognition');
        }
      },
      { type: 'separator' },
      {
        label: 'Exit',
        click: () => {
          this.shutdown();
        }
      }
    ]);

    this.tray.setContextMenu(contextMenu);
    this.tray.on('click', () => {
      if (this.mainWindow) {
        this.mainWindow.isVisible() ? this.mainWindow.hide() : this.mainWindow.show();
      }
    });
  }

  private setupIPC() {
    ipcMain.handle('get-backend-status', async () => {
      return {
        ready: this.backendReady,
        url: 'http://localhost:5000'
      };
    });

    ipcMain.handle('shutdown', async () => {
      this.shutdown();
    });
  }

  private showExitDialog() {
    const { dialog } = require('electron');
    dialog.showMessageBox(this.mainWindow!, {
      type: 'question',
      buttons: ['Exit', 'Cancel'],
      title: 'Exit Gesture Control',
      message: 'Are you sure you want to exit?',
      detail: 'Gesture recognition will stop.'
    }).then((result) => {
      if (result.response === 0) {
        this.shutdown();
      }
    });
  }

  private shutdown() {
    // Stop backend service
    if (this.backendProcess) {
      this.backendProcess.kill();
    }

    // Close window
    if (this.mainWindow) {
      this.mainWindow.destroy();
    }

    // Exit app
    app.quit();
  }

  public start() {
    app.on('ready', () => {
      this.setupTray();
    });

    app.on('window-all-closed', () => {
      if (process.platform !== 'darwin') {
        app.quit();
      }
    });

    app.on('activate', () => {
      if (this.mainWindow === null) {
        this.createWindow();
      }
    });
  }
}

const gestureApp = new GestureControlApp();
gestureApp.start();
```

### Backend Process Management

```python
# backend/main.py - Entry point
import sys
import logging
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from engine import GestureEngine
from controller import WindowsController
from gesture_registry import GestureRegistry
from state_manager import StateManager
from api_server import APIServer
from utils.logger import StructuredLogger

def main():
    # Initialize logger
    logger = StructuredLogger('GestureControl', 'logs/app.log')
    logger.info('Starting Gesture Control Backend')
    
    # Initialize components
    registry = GestureRegistry('config.json')
    engine = GestureEngine('models/cnn_model_keras.h5')
    controller = WindowsController(logger)
    state_manager = StateManager(engine, controller, registry, logger)
    
    # Setup event callbacks
    engine.register_callback(state_manager.on_gesture_detected)
    controller.register_callback(state_manager.on_action_event)
    state_manager.register_callback(lambda event_type, data: logger.info(f'{event_type}: {data}'))
    
    # Start API server
    api_server = APIServer(state_manager, engine, registry, logger, port=5000)
    
    # Register state manager callbacks with API server
    state_manager.register_callback(
        lambda event_type, data: api_server.broadcast_event(event_type, data)
    )
    
    logger.info('API server started on localhost:5000')
    print('API server started')  # Signal to Electron that backend is ready
    
    # Run API server (blocking)
    api_server.run()

if __name__ == '__main__':
    main()
```



## Data Models and Schemas

### Configuration Schema (config.json)

```json
{
  "application": {
    "version": "1.0.0",
    "auto_start": false,
    "logging_level": "INFO"
  },
  "engine": {
    "confidence_threshold": 0.70,
    "smoothing_frames": 20,
    "fps_target": 30,
    "camera_device": 0
  },
  "gestures": {
    "app_switch": {
      "action": "keyboard_shortcut",
      "params": {"keys": ["alt", "tab"]},
      "cooldown_ms": 500,
      "enabled": true,
      "display_name": "App Switch",
      "icon": "app_switch.svg",
      "description": "Switch between open applications"
    },
    "close_window": {
      "action": "keyboard_shortcut",
      "params": {"keys": ["alt", "F4"]},
      "cooldown_ms": 500,
      "enabled": true,
      "display_name": "Close Window",
      "icon": "close_window.svg",
      "description": "Close current window"
    }
  }
}
```

### API Request/Response Schemas

```typescript
// Status Response
interface StatusResponse {
  state: 'stopped' | 'starting' | 'running' | 'pausing' | 'paused' | 'stopping';
  current_gesture: string;
  last_action: string | null;
  uptime: number;
  total_actions: number;
  inference_latency: number;
}

// Config Response
interface ConfigResponse {
  gestures: Record<string, GestureConfig>;
  confidence_threshold: number;
  smoothing_frames: number;
}

interface GestureConfig {
  action: string;
  params: Record<string, any>;
  cooldown_ms: number;
  enabled: boolean;
  display_name: string;
  icon: string;
  description: string;
}

// Action Log Entry
interface ActionLogEntry {
  gesture: string;
  action: string;
  confidence: number;
  timestamp: number;
  success: boolean;
}

// Camera Status
interface CameraStatus {
  connected: boolean;
  fps: number;
  inference_latency_ms: number;
}
```

### WebSocket Event Schemas

```typescript
// Gesture Detected Event
interface GestureDetectedEvent {
  type: 'gesture_detected';
  data: {
    gesture: string;
    confidence: number;
    timestamp: number;
  };
}

// State Changed Event
interface StateChangedEvent {
  type: 'state_changed';
  data: {
    old_state: string;
    new_state: string;
    timestamp: number;
  };
}

// Action Executed Event
interface ActionExecutedEvent {
  type: 'action_executed';
  data: {
    action: string;
    gesture: string;
    timestamp: number;
  };
}

// Error Event
interface ErrorEvent {
  type: 'error';
  data: {
    error_type: string;
    message: string;
    timestamp: number;
  };
}

// Config Updated Event
interface ConfigUpdatedEvent {
  type: 'config_updated';
  data: Record<string, any>;
}
```



## Thread Safety and Concurrency

### Thread Architecture

```
Main Thread (Electron/Tauri)
├── Window Management
├── System Tray
└── IPC Communication

Backend Process (Python)
├── API Server Thread (FastAPI/Uvicorn)
│   ├── REST endpoint handlers
│   └── WebSocket connection manager
├── Engine Thread (Vision Pipeline)
│   ├── Camera capture
│   ├── Frame processing
│   └── CNN inference
└── Main Thread
    ├── State Manager
    ├── Controller
    └── Event coordination
```

### Shared State Protection

**Thread-Safe Mechanisms:**

1. **Locks (RLock)** - Protect state transitions
   ```python
   class StateManager:
       def __init__(self):
           self.lock = threading.RLock()
       
       def start(self):
           with self.lock:
               # Protected state transition
               self._transition_state('starting')
   ```

2. **Thread-Safe Queues** - Decouple components
   ```python
   from queue import Queue
   
   action_queue = Queue()  # Thread-safe
   
   # Engine thread
   action_queue.put(('gesture_detected', gesture_data))
   
   # Main thread
   event_type, data = action_queue.get(timeout=1)
   ```

3. **Atomic Operations** - For simple flags
   ```python
   import threading
   
   running = threading.Event()
   running.set()    # Atomic set
   running.is_set() # Atomic read
   ```

4. **Immutable Data** - Reduce lock contention
   ```python
   from dataclasses import dataclass
   from typing import NamedTuple
   
   @dataclass(frozen=True)
   class GestureEvent:
       gesture: str
       confidence: float
       timestamp: float
   ```

### Event-Driven Communication

```python
class EventBus:
    """
    Central event bus for inter-component communication.
    
    Decouples components and ensures thread safety.
    """
    
    def __init__(self):
        self.subscribers = {}
        self.lock = threading.RLock()
    
    def subscribe(self, event_type: str, callback):
        """Subscribe to event type."""
        with self.lock:
            if event_type not in self.subscribers:
                self.subscribers[event_type] = []
            self.subscribers[event_type].append(callback)
    
    def publish(self, event_type: str, data: dict):
        """Publish event to all subscribers."""
        with self.lock:
            callbacks = self.subscribers.get(event_type, []).copy()
        
        # Call callbacks outside lock to prevent deadlock
        for callback in callbacks:
            try:
                callback(data)
            except Exception as e:
                logger.error(f'Callback error: {str(e)}')

# Usage
event_bus = EventBus()

# Engine publishes gesture events
event_bus.subscribe('gesture_detected', state_manager.on_gesture_detected)
event_bus.subscribe('gesture_detected', api_server.on_gesture_detected)

# Publish from engine thread
event_bus.publish('gesture_detected', {
    'gesture': 'app_switch',
    'confidence': 0.95,
    'timestamp': time.time()
})
```

### Race Condition Prevention

**Critical Section: Gesture Detection to Action Execution**

```python
class StateManager:
    def on_gesture_detected(self, gesture: str, confidence: float):
        """
        Handle gesture detection.
        
        Race conditions to prevent:
        1. Gesture detected while stopping
        2. Cooldown check while updating cooldown
        3. Action log update while reading log
        """
        with self.lock:
            # Check state first (atomic)
            if self.state != 'running':
                return
            
            # Check cooldown (atomic)
            if not self._check_cooldown(gesture):
                return
            
            # Get action (atomic read)
            action_info = self.registry.get_action(gesture)
            if not action_info:
                return
        
        # Execute action outside lock (non-blocking)
        success = self.controller.execute_action(
            action_info['action'],
            action_info['params']
        )
        
        # Update state after execution (atomic)
        with self.lock:
            if success:
                self.last_action = gesture
                self.last_action_time = time.time()
                self.cooldown_tracker[gesture] = time.time() + (action_info['cooldown_ms'] / 1000)
                self.action_log.append({...})
```



## Error Handling and Recovery

### Camera Error Recovery

```python
class GestureEngine:
    def _process_loop(self):
        """Main processing loop with error recovery."""
        consecutive_errors = 0
        max_consecutive_errors = 10
        
        while self.running:
            try:
                ret, frame = self.camera.read()
                
                if not ret:
                    consecutive_errors += 1
                    if consecutive_errors >= max_consecutive_errors:
                        self._emit_event('camera_error', {
                            'message': 'Camera disconnected',
                            'consecutive_errors': consecutive_errors
                        })
                        self._attempt_camera_reconnect()
                        consecutive_errors = 0
                    continue
                
                # Reset error counter on successful frame
                consecutive_errors = 0
                
                # Process frame
                gesture, confidence = self._process_frame(frame)
                confirmed_gesture = self._apply_temporal_smoothing(gesture, confidence)
                
                if confirmed_gesture:
                    self._emit_event('gesture_detected', confirmed_gesture)
            
            except Exception as e:
                self.logger.error(f'Processing error: {str(e)}')
                self._emit_event('processing_error', {'error': str(e)})
    
    def _attempt_camera_reconnect(self, max_attempts: int = 5):
        """Attempt to reconnect to camera."""
        for attempt in range(max_attempts):
            try:
                if self.camera:
                    self.camera.release()
                
                self.camera = cv2.VideoCapture(0)
                if self.camera.isOpened():
                    self.logger.info(f'Camera reconnected on attempt {attempt + 1}')
                    self._emit_event('camera_connected', {})
                    return True
            except Exception as e:
                self.logger.warning(f'Reconnect attempt {attempt + 1} failed: {str(e)}')
                time.sleep(1)
        
        self.logger.error('Failed to reconnect camera after max attempts')
        return False
```

### API Error Responses

```python
from fastapi import HTTPException, status

class APIServer:
    def setup_routes(self):
        @self.app.post('/api/start')
        async def start():
            try:
                success = self.state_manager.start()
                if not success:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail='Cannot start from current state'
                    )
                return {'success': True, 'state': self.state_manager.state}
            except Exception as e:
                self.logger.error(f'Start failed: {str(e)}')
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=str(e)
                )
        
        @self.app.exception_handler(Exception)
        async def general_exception_handler(request, exc):
            self.logger.error(f'Unhandled exception: {str(exc)}')
            return {
                'error': 'Internal server error',
                'detail': str(exc) if not isinstance(exc, HTTPException) else exc.detail
            }
```

### Graceful Shutdown Sequence

```python
class Application:
    def __init__(self):
        self.shutdown_event = threading.Event()
        self.shutdown_timeout = 5  # seconds
    
    def shutdown(self):
        """
        Graceful shutdown sequence.
        
        Steps:
        1. Signal shutdown to all components
        2. Stop accepting new gestures
        3. Wait for in-flight actions (max 5s)
        4. Close API server and WebSocket
        5. Release camera
        6. Terminate threads
        7. Flush logs
        """
        self.logger.info('Initiating graceful shutdown')
        self.shutdown_event.set()
        
        start_time = time.time()
        
        try:
            # Step 1: Stop accepting new gestures
            self.state_manager.stop()
            
            # Step 2: Wait for in-flight actions
            while self.state_manager.last_action_time > time.time() - 1:
                if time.time() - start_time > self.shutdown_timeout:
                    self.logger.warning('Shutdown timeout: forcing termination')
                    break
                time.sleep(0.1)
            
            # Step 3: Close API server
            self.api_server.shutdown()
            
            # Step 4: Release resources
            self.engine.stop()
            
            # Step 5: Flush logs
            self.logger.info('Shutdown complete')
            
            return 0
        
        except Exception as e:
            self.logger.error(f'Shutdown error: {str(e)}')
            return 1
    
    def handle_signal(self, signum, frame):
        """Handle Ctrl+C and system signals."""
        self.logger.info(f'Received signal {signum}')
        exit_code = self.shutdown()
        sys.exit(exit_code)
```

### Service Restart Logic

```python
class ServiceManager:
    def __init__(self, max_restart_attempts: int = 3):
        self.max_restart_attempts = max_restart_attempts
        self.restart_count = 0
        self.last_restart_time = 0
        self.restart_cooldown = 5  # seconds
    
    def handle_service_crash(self, error: Exception):
        """Handle unexpected service crash."""
        current_time = time.time()
        
        # Check restart cooldown
        if current_time - self.last_restart_time < self.restart_cooldown:
            self.logger.warning('Restart cooldown active, skipping restart')
            return False
        
        # Check restart attempts
        if self.restart_count >= self.max_restart_attempts:
            self.logger.error('Max restart attempts exceeded')
            return False
        
        self.restart_count += 1
        self.last_restart_time = current_time
        
        self.logger.info(f'Attempting restart {self.restart_count}/{self.max_restart_attempts}')
        
        try:
            self.restart_service()
            self.restart_count = 0  # Reset on successful restart
            return True
        except Exception as e:
            self.logger.error(f'Restart failed: {str(e)}')
            return False
    
    def restart_service(self):
        """Restart the service."""
        # Implementation depends on deployment model
        pass
```



## Performance Considerations

### Frame Processing Pipeline Optimization

```python
class OptimizedEngine:
    """
    Optimized vision pipeline for 30 FPS @ <50ms latency.
    """
    
    def __init__(self):
        self.frame_buffer = None
        self.model = None
        self.use_gpu = self._check_gpu_availability()
    
    def _check_gpu_availability(self) -> bool:
        """Check if GPU acceleration is available."""
        try:
            import tensorflow as tf
            gpus = tf.config.list_physical_devices('GPU')
            if gpus:
                print(f'GPU available: {len(gpus)} device(s)')
                return True
        except:
            pass
        return False
    
    def _process_frame(self, frame: np.ndarray) -> tuple:
        """
        Optimized frame processing.
        
        Optimizations:
        1. Reuse buffers (avoid allocations)
        2. Batch operations (vectorized)
        3. Early exit on failures
        4. GPU acceleration for inference
        """
        start_time = time.perf_counter()
        
        # Step 1: Skin detection (optimized with OpenCV)
        hand_region = self._fast_skin_detect(frame)
        if hand_region is None:
            return 'nothing', 0.0
        
        # Step 2: Resize with interpolation (faster than cv2.resize)
        if self.frame_buffer is None:
            self.frame_buffer = np.zeros((1, 50, 50, 1), dtype=np.float32)
        
        resized = cv2.resize(hand_region, (50, 50), interpolation=cv2.INTER_LINEAR)
        self.frame_buffer[0, :, :, 0] = resized.astype(np.float32) / 255.0
        
        # Step 3: Inference (GPU accelerated if available)
        predictions = self.model.predict(self.frame_buffer, verbose=0)
        gesture_idx = np.argmax(predictions[0])
        confidence = float(predictions[0][gesture_idx])
        
        elapsed = (time.perf_counter() - start_time) * 1000
        self.inference_latency = elapsed
        
        if confidence < self.confidence_threshold:
            return 'nothing', 0.0
        
        return self._idx_to_gesture(gesture_idx), confidence
    
    def _fast_skin_detect(self, frame: np.ndarray) -> np.ndarray:
        """
        Fast skin detection using YCrCb with optimizations.
        
        Optimizations:
        1. Use cv2.inRange (vectorized)
        2. Minimal morphological operations
        3. Early exit if no skin found
        """
        # Convert to YCrCb (single operation)
        ycrcb = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb)
        
        # Vectorized range check
        mask = cv2.inRange(ycrcb, (0, 130, 77), (255, 170, 127))
        
        # Minimal morphology
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=1)
        
        # Find largest contour
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return None
        
        largest = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest)
        
        # Extract region
        hand_region = frame[y:y+h, x:x+w]
        return cv2.cvtColor(hand_region, cv2.COLOR_BGR2GRAY) if hand_region.size > 0 else None
```

### GPU Acceleration Support

```python
import tensorflow as tf

class GPUAcceleratedModel:
    """
    Load and optimize model for GPU inference.
    """
    
    def __init__(self, model_path: str):
        # Enable GPU memory growth to avoid OOM
        gpus = tf.config.list_physical_devices('GPU')
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
        
        # Load model with optimization
        self.model = tf.keras.models.load_model(model_path)
        
        # Convert to TensorFlow Lite for faster inference (optional)
        self.use_tflite = False
        try:
            converter = tf.lite.TFLiteConverter.from_keras_model(self.model)
            converter.optimizations = [tf.lite.Optimize.DEFAULT]
            self.tflite_model = converter.convert()
            self.use_tflite = True
        except:
            pass
    
    def predict(self, input_data: np.ndarray) -> np.ndarray:
        """Predict with GPU acceleration."""
        if self.use_tflite:
            # TensorFlow Lite inference (faster)
            interpreter = tf.lite.Interpreter(model_content=self.tflite_model)
            interpreter.allocate_tensors()
            
            input_details = interpreter.get_input_details()
            output_details = interpreter.get_output_details()
            
            interpreter.set_tensor(input_details[0]['index'], input_data)
            interpreter.invoke()
            
            return interpreter.get_tensor(output_details[0]['index'])
        else:
            # Standard Keras inference (GPU accelerated)
            return self.model.predict(input_data, verbose=0)
```

### Memory Management

```python
class MemoryOptimizedEngine:
    """
    Manage memory usage to stay under 500MB.
    """
    
    def __init__(self):
        self.max_memory_mb = 500
        self.frame_buffer_size = 30  # Frames to keep
        self.action_log_size = 1000  # Entries to keep
    
    def monitor_memory(self):
        """Monitor and log memory usage."""
        import psutil
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        
        if memory_mb > self.max_memory_mb:
            logger.warning(f'Memory usage high: {memory_mb:.1f}MB')
            self._cleanup_memory()
        
        return memory_mb
    
    def _cleanup_memory(self):
        """Clean up memory if usage is high."""
        import gc
        
        # Clear caches
        self.frame_buffer.clear()
        
        # Force garbage collection
        gc.collect()
        
        logger.info('Memory cleanup performed')
```

### API Response Time Optimization

```python
from fastapi import BackgroundTasks

class OptimizedAPIServer:
    """
    Optimize API response times.
    """
    
    @self.app.get('/api/status')
    async def get_status():
        """
        Return cached status (updated every 100ms).
        
        Avoids lock contention on every request.
        """
        return self.cached_status
    
    @self.app.post('/api/config')
    async def update_config(config: dict, background_tasks: BackgroundTasks):
        """
        Return immediately, persist in background.
        """
        # Update in-memory config
        self._apply_config(config)
        
        # Persist to disk in background
        background_tasks.add_task(self.registry.save_config)
        
        return {'success': True}
    
    def _update_cached_status(self):
        """Update cached status every 100ms."""
        while True:
            self.cached_status = self.state_manager.get_status()
            time.sleep(0.1)
```



## Security Design

### Localhost-Only API Binding

```python
from fastapi import FastAPI
import uvicorn

class SecureAPIServer:
    """
    Ensure API only listens on localhost.
    """
    
    def __init__(self):
        self.app = FastAPI()
        self.setup_security()
    
    def setup_security(self):
        """Configure security settings."""
        # Only bind to localhost
        self.host = '127.0.0.1'
        self.port = 5000
        
        # Disable CORS for external origins
        from fastapi.middleware.cors import CORSMiddleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=['http://localhost:3000', 'http://127.0.0.1:3000'],
            allow_credentials=True,
            allow_methods=['GET', 'POST'],
            allow_headers=['*']
        )
    
    def run(self):
        """Start server with security settings."""
        uvicorn.run(
            self.app,
            host=self.host,
            port=self.port,
            log_level='info',
            # Disable external access
            server_header=False
        )
```

### Input Validation

```python
from pydantic import BaseModel, validator

class ConfigUpdate(BaseModel):
    """Validate configuration updates."""
    
    confidence_threshold: float = None
    smoothing_frames: int = None
    cooldown_ms: int = None
    
    @validator('confidence_threshold')
    def validate_confidence(cls, v):
        if v is not None and not (0.5 <= v <= 0.95):
            raise ValueError('Confidence must be between 0.5 and 0.95')
        return v
    
    @validator('smoothing_frames')
    def validate_smoothing(cls, v):
        if v is not None and not (5 <= v <= 100):
            raise ValueError('Smoothing frames must be between 5 and 100')
        return v
    
    @validator('cooldown_ms')
    def validate_cooldown(cls, v):
        if v is not None and not (0 <= v <= 5000):
            raise ValueError('Cooldown must be between 0 and 5000ms')
        return v

@app.post('/api/config')
async def update_config(config: ConfigUpdate):
    """Update configuration with validation."""
    try:
        # Pydantic validates automatically
        if config.confidence_threshold:
            engine.confidence_threshold = config.confidence_threshold
        # ... other updates
        return {'success': True}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

### No External Data Transmission

```python
class DataProtection:
    """
    Ensure no data leaves the local machine.
    """
    
    @staticmethod
    def validate_no_external_calls():
        """
        Verify no external network calls are made.
        
        Allowed:
        - localhost:5000 (API)
        - Camera device (local)
        - File system (local)
        
        Blocked:
        - External HTTP/HTTPS
        - DNS queries (except localhost)
        - Network sockets to external IPs
        """
        pass
    
    @staticmethod
    def sanitize_logs(log_entry: dict) -> dict:
        """
        Remove sensitive data from logs.
        
        Never log:
        - Video frames
        - Personal data
        - System paths (except app paths)
        """
        sanitized = {
            'gesture': log_entry.get('gesture'),
            'action': log_entry.get('action'),
            'confidence': log_entry.get('confidence'),
            'timestamp': log_entry.get('timestamp'),
            'success': log_entry.get('success')
        }
        return sanitized
```

### Configuration File Permissions

```python
import os
import stat

class SecureConfigManager:
    """
    Manage configuration file permissions.
    """
    
    def __init__(self, config_path: str):
        self.config_path = config_path
        self._ensure_secure_permissions()
    
    def _ensure_secure_permissions(self):
        """
        Set restrictive permissions on config file.
        
        Unix: 0o600 (rw-------)
        Windows: Only current user can read/write
        """
        try:
            if os.path.exists(self.config_path):
                # Unix-like systems
                os.chmod(self.config_path, stat.S_IRUSR | stat.S_IWUSR)
                
                # Windows: Set ACL (requires pywin32)
                if os.name == 'nt':
                    self._set_windows_permissions()
        except Exception as e:
            logger.warning(f'Failed to set permissions: {str(e)}')
    
    def _set_windows_permissions(self):
        """Set Windows-specific permissions."""
        try:
            import win32security
            import win32api
            
            # Get current user SID
            user = win32api.GetUserName()
            
            # Set permissions (implementation depends on pywin32)
            # This is a placeholder
            logger.info(f'Windows permissions set for {user}')
        except ImportError:
            logger.warning('pywin32 not available, skipping Windows permissions')
```

