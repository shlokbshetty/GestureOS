# Implementation Plan: Gesture Control Desktop Application

## Overview

This implementation plan transforms the fragmented Gesture Control ACT project into a production-ready Windows desktop application. The approach follows a layered architecture: Python backend service for gesture recognition and Windows automation, React frontend dashboard for monitoring and control, and Electron/Tauri wrapper for native desktop integration. Implementation proceeds from core infrastructure through vision pipeline, state management, API layer, frontend UI, and finally desktop packaging.

## Tasks

- [x] 1. Project Setup and Infrastructure
  - [x] 1.1 Create project directory structure and Python package layout
    - Create `backend/`, `frontend/`, `desktop/` directories
    - Create `backend/utils/`, `backend/models/` subdirectories
    - Initialize Python virtual environment and requirements.txt
    - _Requirements: 1.0, 5.0, 14.0_

  - [x] 1.2 Set up Python dependencies and environment
    - Install core dependencies: opencv-python, tensorflow, fastapi, uvicorn, pynput, pyautogui
    - Install development dependencies: pytest, black, flake8
    - Create .env file for configuration paths
    - _Requirements: 1.0, 5.0_

  - [x] 1.3 Create configuration management system
    - Implement `utils/config.py` with JSON-based configuration loading
    - Create default `config.json` with gesture mappings, thresholds, and paths
    - Implement configuration validation and error handling
    - _Requirements: 12.0, 2.0_

  - [x] 1.4 Set up structured logging system
    - Implement `utils/logger.py` with RotatingFileHandler
    - Configure log rotation (10MB max, 5 files kept)
    - Create logs directory and initialize logging on startup
    - _Requirements: 8.0_

- [ ] 2. Core Vision Pipeline (Gesture Engine)
  - [-] 2.1 Implement camera capture and frame processing
    - Create `engine.py` with GestureEngine class
    - Implement camera initialization with fallback to alternate device
    - Implement 30 FPS frame capture loop with timing control
    - Add camera error detection and event emission
    - _Requirements: 1.1, 1.8, 13.0_

  - [-] 2.2 Implement YCrCb skin detection algorithm
    - Create `SkinDetector` class in engine.py
    - Implement YCrCb color space conversion and thresholding
    - Add morphological operations (close, open) for mask cleanup
    - Implement hand region extraction with bounding box and padding
    - _Requirements: 1.2, 1.3_

  - [-] 2.3 Implement CNN model loading and inference
    - Load pre-trained CNN model (cnn_model_keras.h5) using TensorFlow
    - Implement image normalization (50x50, 0-1 range)
    - Implement CNN inference with prediction extraction
    - Track inference latency for performance monitoring
    - _Requirements: 1.4, 17.0_

  - [~] 2.4 Implement confidence threshold filtering
    - Add confidence threshold check (default 70%)
    - Return 'nothing' gesture for low-confidence predictions
    - Make threshold configurable via API
    - _Requirements: 1.5_

  - [~] 2.5 Implement temporal smoothing algorithm
    - Create `utils/smoothing.py` with TemporalSmoother class
    - Implement frame buffer tracking (deque with max length)
    - Implement gesture confirmation logic (20+ consecutive frames)
    - Add buffer reset on different gesture detection
    - _Requirements: 1.6, 7.0_

  - [~] 2.6 Implement gesture event emission system
    - Add event callback registration to GestureEngine
    - Emit gesture_detected events with gesture name, confidence, timestamp
    - Emit camera_error events on camera failures
    - Emit performance_warning events on low frame rate
    - _Requirements: 1.7, 1.9_

- [ ] 3. Gesture Registry and Configuration
  - [-] 3.1 Implement gesture registry data structure
    - Create `gesture_registry.py` with GestureRegistry class
    - Define DEFAULT_GESTURES mapping with all 9 gestures
    - Include metadata: display_name, icon, description, cooldown_ms, enabled
    - _Requirements: 2.1, 2.2, 2.7_

  - [~] 3.2 Implement gesture configuration persistence
    - Implement JSON-based configuration loading from gestures.json
    - Implement configuration saving with proper formatting
    - Add file not found handling with default configuration fallback
    - _Requirements: 2.3, 2.4_

  - [~] 3.3 Implement gesture action mapping and retrieval
    - Implement get_action() method returning action type, params, cooldown
    - Implement gesture enable/disable functionality
    - Implement update_gesture() for runtime configuration changes
    - _Requirements: 2.5, 2.6, 2.7_

- [ ] 4. Windows System Controller
  - [-] 4.1 Implement keyboard automation
    - Create `controller.py` with WindowsController class
    - Implement keyboard shortcut execution (Alt+Tab, Alt+F4)
    - Implement single key presses (Space, Print Screen)
    - Use pynput for cross-platform compatibility
    - _Requirements: 3.2, 3.3, 3.9_

  - [~] 4.2 Implement media key handling
    - Implement media key execution (Volume Up, Volume Down, Play/Pause)
    - Use pynput media key constants
    - Add error handling for unsupported media keys
    - _Requirements: 3.5, 3.6_

  - [~] 4.3 Implement mouse control
    - Implement mouse scroll functionality (up/down with units)
    - Implement mouse movement (for future features)
    - Use pyautogui for mouse operations
    - _Requirements: 3.7, 3.8_

  - [~] 4.4 Implement action execution with error handling
    - Implement execute_action() method with action type dispatch
    - Add try-catch error handling with logging
    - Emit action_executed and action_failed events
    - _Requirements: 3.1, 3.10_

- [ ] 5. State Manager and Application Lifecycle
  - [ ] 5.1 Implement state machine and transitions
    - Create `state_manager.py` with StateManager class
    - Implement state constants: stopped, starting, running, pausing, paused, stopping
    - Implement state transition logic with validation
    - Emit state_changed events on transitions
    - _Requirements: 4.1, 4.2, 4.6_

  - [~] 5.2 Implement start/stop lifecycle methods
    - Implement start() method: transition to starting, initialize engine, transition to running
    - Implement stop() method: transition to stopping, graceful shutdown, transition to stopped
    - Add timeout handling for in-flight actions (max 5 seconds)
    - _Requirements: 4.2, 4.3, 10.0_

  - [~] 5.3 Implement pause/resume functionality
    - Implement pause() method: transition to pausing, pause engine, transition to paused
    - Implement resume() method: transition to running, resume engine
    - Maintain state consistency during pause/resume cycles
    - _Requirements: 4.4, 4.5_

  - [~] 5.4 Implement cooldown tracking system
    - Create `utils/debounce.py` with CooldownTracker class
    - Implement cooldown period tracking per gesture
    - Implement cooldown expiry checking and cleanup
    - _Requirements: 3.11, 7.4, 7.5, 7.6_

  - [~] 5.5 Implement gesture detection event handling
    - Implement on_gesture_detected() callback handler
    - Integrate cooldown checking before action execution
    - Integrate gesture registry action lookup
    - Log action execution with gesture name and confidence
    - _Requirements: 4.7, 3.1_

  - [~] 5.6 Implement action logging and status tracking
    - Implement action_log deque (max 1000 entries)
    - Log action details: gesture, action type, confidence, timestamp, success
    - Implement get_action_log() with limit parameter
    - Implement get_status() returning current state and metrics
    - _Requirements: 4.7, 8.2, 8.3_

  - [~] 5.7 Implement thread-safe state access
    - Add threading.RLock for state protection
    - Protect all state modifications with lock acquisition
    - Implement thread-safe callback emission
    - _Requirements: 9.1, 9.2, 9.3_

- [ ] 6. REST API Server
  - [~] 6.1 Set up FastAPI application and middleware
    - Create `api_server.py` with FastAPI app initialization
    - Configure CORS middleware for localhost only
    - Set up error handling middleware
    - _Requirements: 5.1, 5.12, 18.1_

  - [~] 6.2 Implement status and control endpoints
    - Implement GET /api/status endpoint returning application state
    - Implement POST /api/start endpoint
    - Implement POST /api/stop endpoint
    - Implement POST /api/pause endpoint
    - Implement POST /api/resume endpoint
    - _Requirements: 5.2, 5.3, 5.4, 5.5, 5.6_

  - [~] 6.3 Implement configuration endpoints
    - Implement GET /api/config endpoint returning gesture registry and thresholds
    - Implement POST /api/config endpoint for configuration updates
    - Add configuration validation before persistence
    - Broadcast config_updated events to WebSocket clients
    - _Requirements: 5.7, 5.8_

  - [~] 6.4 Implement logging and monitoring endpoints
    - Implement GET /api/logs endpoint with limit parameter
    - Implement GET /api/camera-status endpoint
    - Add pagination support for logs
    - _Requirements: 5.9, 5.10_

  - [~] 6.5 Implement WebSocket streaming
    - Implement WebSocket endpoint at /ws
    - Implement client connection tracking
    - Implement broadcast_event() for multi-client messaging
    - Add error handling for disconnected clients
    - _Requirements: 5.11, 11.6_

  - [~] 6.6 Implement event broadcasting system
    - Connect engine events to WebSocket broadcasting
    - Connect state manager events to WebSocket broadcasting
    - Connect controller events to WebSocket broadcasting
    - Implement event message format with type, data, timestamp
    - _Requirements: 5.11_

  - [~] 6.7 Implement API server startup and lifecycle
    - Implement run() method using uvicorn
    - Configure server to listen on localhost:5000 only
    - Add graceful shutdown handling
    - _Requirements: 5.1, 18.1_

- [ ] 7. Application Integration and Main Entry Point
  - [~] 7.1 Create main application orchestrator
    - Create `main.py` with application initialization
    - Instantiate all components: Engine, Controller, Registry, StateManager, APIServer
    - Wire up event callbacks between components
    - Implement graceful shutdown signal handling (Ctrl+C)
    - _Requirements: 10.0, 10.1, 10.2_

  - [~] 7.2 Implement graceful shutdown sequence
    - Implement signal handlers for SIGINT and SIGTERM
    - Implement shutdown sequence: stop accepting gestures, wait for in-flight actions, close resources
    - Implement thread termination with timeout (5 seconds)
    - Implement exit code handling (0 for success, 1 for timeout)
    - _Requirements: 10.0, 10.3, 10.4, 10.5, 10.6, 10.7, 10.8, 10.9, 10.10_

  - [~] 7.3 Implement Windows service integration
    - Create service wrapper using pywin32 or nssm
    - Implement --install-service command-line flag
    - Implement --uninstall-service command-line flag
    - Configure service to start on boot and run in background
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5_

  - [~] 7.4 Implement system tray integration
    - Create system tray icon using pystray
    - Implement Start/Stop controls in tray menu
    - Implement Open Dashboard option
    - Implement Exit option with graceful shutdown
    - _Requirements: 11.8_

- [ ] 8. Frontend Dashboard - Setup and Core Components
  - [~] 8.1 Set up React project with TypeScript and Tailwind
    - Create React app with TypeScript template
    - Install Tailwind CSS and configure
    - Set up project structure: components/, pages/, context/, styles/
    - Configure build and development servers
    - _Requirements: 6.0, 6.1_

  - [~] 8.2 Create WebSocket context and connection management
    - Create `context/WebSocketContext.tsx` with WebSocket provider
    - Implement WebSocket connection to localhost:5000/ws
    - Implement automatic reconnection with 3-second retry
    - Implement message parsing and state updates
    - _Requirements: 6.2, 5.11_

  - [~] 8.3 Create root App component with layout
    - Create `App.tsx` with global styling and layout
    - Implement connection loading state with spinner
    - Apply Neo-style dark theme with glassmorphism
    - _Requirements: 6.1, 6.2_

  - [~] 8.4 Create Dashboard main layout component
    - Create `pages/Dashboard.tsx` with three-column grid layout
    - Implement header with logo and status indicator
    - Implement responsive grid for control, camera, and config panels
    - _Requirements: 6.3, 6.4, 6.5, 6.6, 6.7, 6.8, 6.9, 6.10, 6.11, 6.12_

- [ ] 9. Frontend Dashboard - Control and Display Components
  - [~] 9.1 Create ControlPanel component
    - Create `components/ControlPanel.tsx` with Start/Stop/Pause/Resume buttons
    - Implement button state logic based on application state
    - Apply Neo-style button styling with color coding
    - _Requirements: 6.3, 6.4_

  - [~] 9.2 Create GestureDisplay component
    - Create `components/GestureDisplay.tsx` showing current gesture
    - Implement gesture icon mapping (emoji or SVG)
    - Display gesture name and confidence percentage
    - _Requirements: 6.5_

  - [~] 9.3 Create CameraFeed component
    - Create `components/CameraFeed.tsx` with live camera preview
    - Implement MJPEG stream from backend or canvas rendering
    - Display hand detection region and skin mask overlay
    - _Requirements: 6.6_

  - [~] 9.4 Create ActionLog component
    - Create `components/ActionLog.tsx` displaying recent actions
    - Implement scrollable list of last 20 actions
    - Display gesture name, action type, timestamp, and confidence
    - _Requirements: 6.7_

- [ ] 10. Frontend Dashboard - Configuration and Statistics
  - [~] 10.1 Create ConfigPanel component
    - Create `components/ConfigPanel.tsx` with configuration controls
    - Implement cooldown slider (0-5000ms)
    - Implement confidence threshold slider (50-95%)
    - Implement gesture enable/disable toggles
    - _Requirements: 6.8, 6.9, 6.11, 6.13_

  - [~] 10.2 Create StatisticsPanel component
    - Create `components/StatisticsPanel.tsx` displaying metrics
    - Display uptime, total gestures detected, total actions executed
    - Display average inference latency
    - _Requirements: 6.12_

  - [~] 10.3 Create error notification system
    - Create `components/ErrorNotification.tsx` for error display
    - Implement error message display with recovery options
    - Implement camera disconnection handling with retry button
    - _Requirements: 6.15, 13.4, 13.5_

  - [~] 10.4 Create camera status indicator
    - Create `components/CameraStatus.tsx` showing connection status
    - Display frame rate and connection health
    - _Requirements: 6.10_

- [ ] 11. Frontend Dashboard - Accessibility Features
  - [~] 11.1 Implement keyboard navigation
    - Add Tab navigation support to all interactive elements
    - Implement Enter key activation for buttons
    - Implement Escape key for closing modals
    - _Requirements: 20.6_

  - [~] 11.2 Implement ARIA labels and semantic HTML
    - Add ARIA labels to all buttons and controls
    - Use semantic HTML elements (button, nav, main, section)
    - Implement screen reader compatibility
    - _Requirements: 20.7_

  - [~] 11.3 Implement high contrast mode
    - Create high contrast color scheme option
    - Implement toggle for high contrast in settings
    - Ensure text contrast meets WCAG AA standards
    - _Requirements: 20.5_

  - [~] 11.4 Implement audio feedback system
    - Create audio feedback for gesture detection (optional, configurable)
    - Create audio feedback for action execution
    - Implement volume control for audio feedback
    - _Requirements: 20.8_

- [ ] 12. Desktop Wrapper (Electron/Tauri)
  - [~] 12.1 Set up Electron application structure
    - Create Electron main process in `desktop/main.js`
    - Create preload script for IPC communication
    - Configure window creation and lifecycle
    - _Requirements: 15.1, 15.2, 15.3_

  - [~] 12.2 Implement backend process management
    - Implement Python backend process spawning
    - Implement health monitoring and auto-restart on crash
    - Implement graceful shutdown of backend on app close
    - _Requirements: 15.2, 15.9_

  - [~] 12.3 Implement system tray integration
    - Create system tray icon with context menu
    - Implement Start/Stop controls in tray
    - Implement Open Dashboard option
    - Implement Exit option
    - _Requirements: 15.6, 15.7_

  - [~] 12.4 Implement window lifecycle management
    - Implement window creation and show/hide logic
    - Implement close confirmation dialog
    - Implement minimize to tray functionality
    - _Requirements: 15.4, 15.5_

  - [~] 12.5 Implement auto-start configuration
    - Implement auto-start on system boot option
    - Store auto-start preference in configuration
    - Use Windows registry or startup folder
    - _Requirements: 15.8_

- [ ] 13. Installation and Packaging
  - [~] 13.1 Create Windows installer
    - Set up NSIS or Inno Setup installer configuration
    - Configure installer to extract backend, frontend, and dependencies
    - Create Start Menu shortcuts
    - Create Desktop shortcuts
    - _Requirements: 14.1, 14.2, 14.3, 14.4_

  - [~] 13.2 Implement dependency checking and installation
    - Check for Python 3.9+ installation
    - Check for Visual C++ redistributables
    - Implement automatic dependency installation
    - _Requirements: 14.8_

  - [~] 13.3 Implement Windows registry integration
    - Register application in Add/Remove Programs
    - Create uninstall entry
    - Store application paths in registry
    - _Requirements: 14.5_

  - [~] 13.4 Implement silent installation support
    - Add --silent command-line flag support
    - Implement non-interactive installation mode
    - _Requirements: 14.9_

  - [~] 13.5 Implement uninstaller
    - Create uninstaller that removes all files
    - Remove registry entries
    - Remove Start Menu and Desktop shortcuts
    - _Requirements: 14.7_

- [ ] 14. Documentation and Testing
  - [~] 14.1 Create comprehensive README documentation
    - Write installation instructions for end users
    - Write system requirements section
    - Write quick start guide
    - Write configuration guide with examples
    - _Requirements: 16.1, 16.2, 16.3, 16.4_

  - [~] 14.2 Create troubleshooting documentation
    - Document common issues and solutions
    - Document camera detection troubleshooting
    - Document low accuracy troubleshooting
    - _Requirements: 16.5_

  - [~] 14.3 Create developer documentation
    - Write architecture overview
    - Write module descriptions
    - Write contribution guidelines
    - _Requirements: 16.6_

  - [~] 14.4 Create API documentation
    - Document all REST endpoints with examples
    - Document WebSocket event formats
    - Document request/response schemas
    - _Requirements: 16.7_

  - [~] 14.5 Create performance benchmarks documentation
    - Document inference latency benchmarks
    - Document frame rate benchmarks
    - Document memory usage benchmarks
    - _Requirements: 16.8_

  - [~] 14.6 Add inline code comments
    - Add comments to complex algorithms (skin detection, temporal smoothing)
    - Add comments to state machine logic
    - Add comments to thread-safe operations
    - _Requirements: 16.10_

  - [~] 14.7 Create unit tests for core modules
    - Create tests for GestureEngine frame processing
    - Create tests for SkinDetector algorithm
    - Create tests for StateManager state transitions
    - Create tests for CooldownTracker
    - _Requirements: 22.1, 22.4_

  - [~] 14.8 Create integration tests
    - Create end-to-end gesture detection tests
    - Create action execution tests
    - Create API endpoint tests
    - _Requirements: 22.2_

  - [~] 14.9 Create performance tests
    - Create inference latency tests
    - Create frame rate tests
    - Create memory usage tests
    - _Requirements: 22.3_

  - [~] 14.10 Set up test runner and CI/CD
    - Configure pytest for test execution
    - Create test runner script
    - Achieve 80% code coverage for critical modules
    - _Requirements: 22.6, 22.4_

- [~] 15. Checkpoint - Core Backend Complete
  - Ensure all backend modules are implemented and tested
  - Verify gesture detection pipeline works end-to-end
  - Verify API server responds to requests
  - Ask the user if questions arise before proceeding to frontend integration

- [ ] 16. Frontend Integration and Testing
  - [~] 16.1 Integrate frontend with backend API
    - Connect all API calls to backend endpoints
    - Implement error handling for API failures
    - Implement loading states during API calls
    - _Requirements: 6.2, 5.0_

  - [~] 16.2 Test WebSocket real-time updates
    - Verify gesture_detected events update UI
    - Verify state_changed events update UI
    - Verify action_log updates in real-time
    - _Requirements: 6.2, 5.11_

  - [~] 16.3 Test configuration updates
    - Verify slider changes persist to backend
    - Verify gesture toggles persist to backend
    - Verify configuration changes take effect immediately
    - _Requirements: 6.13, 5.8_

  - [~] 16.4 Test responsive design
    - Verify dashboard works on 1920x1080 resolution
    - Verify dashboard works on higher resolutions
    - Verify all panels are visible and accessible
    - _Requirements: 6.16_

- [ ] 17. Desktop Wrapper Integration and Testing
  - [~] 17.1 Test Electron application startup
    - Verify backend process starts correctly
    - Verify frontend loads in Electron window
    - Verify WebSocket connection works
    - _Requirements: 15.1, 15.2, 15.3_

  - [~] 17.2 Test system tray functionality
    - Verify tray icon appears
    - Verify Start/Stop controls work from tray
    - Verify Open Dashboard works
    - Verify Exit works with graceful shutdown
    - _Requirements: 15.6, 15.7_

  - [~] 17.3 Test window lifecycle
    - Verify minimize to tray works
    - Verify close confirmation dialog appears
    - Verify graceful shutdown on close
    - _Requirements: 15.4, 15.5_

  - [~] 17.4 Test auto-start functionality
    - Verify auto-start option can be toggled
    - Verify application starts on system boot when enabled
    - _Requirements: 15.8_

- [ ] 18. Installer Testing and Validation
  - [~] 18.1 Test installer execution
    - Verify installer extracts all files correctly
    - Verify shortcuts are created
    - Verify registry entries are created
    - _Requirements: 14.1, 14.2, 14.3, 14.4, 14.5_

  - [~] 18.2 Test dependency installation
    - Verify Python 3.9+ is installed or installed by installer
    - Verify Visual C++ redistributables are installed
    - _Requirements: 14.8_

  - [~] 18.3 Test uninstaller
    - Verify uninstaller removes all files
    - Verify registry entries are removed
    - Verify shortcuts are removed
    - _Requirements: 14.7_

  - [~] 18.4 Test silent installation
    - Verify --silent flag works
    - Verify installation completes without user interaction
    - _Requirements: 14.9_

- [ ] 19. End-to-End Testing and Validation
  - [~] 19.1 Test complete gesture recognition workflow
    - Verify camera captures frames at 30 FPS
    - Verify skin detection isolates hand region
    - Verify CNN inference produces predictions
    - Verify temporal smoothing confirms gestures
    - Verify actions execute on gesture confirmation
    - _Requirements: 1.0, 3.0, 7.0_

  - [~] 19.2 Test all gesture-to-action mappings
    - Test app_switch gesture executes Alt+Tab
    - Test close_window gesture executes Alt+F4
    - Test play_pause gesture executes Space
    - Test volume_up gesture executes Volume Up key
    - Test volume_down gesture executes Volume Down key
    - Test scroll_up gesture executes mouse scroll up
    - Test scroll_down gesture executes mouse scroll down
    - Test screenshot gesture executes Print Screen
    - _Requirements: 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9_

  - [~] 19.3 Test state machine transitions
    - Test stopped -> starting -> running transition
    - Test running -> pausing -> paused transition
    - Test paused -> running transition
    - Test running -> stopping -> stopped transition
    - Test error handling and recovery
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.8_

  - [~] 19.4 Test cooldown and debounce system
    - Verify cooldown prevents rapid re-triggering
    - Verify cooldown period is configurable
    - Verify cooldown expires correctly
    - _Requirements: 7.0, 3.11_

  - [~] 19.5 Test error handling and recovery
    - Test camera disconnection and reconnection
    - Test API server error responses
    - Test graceful shutdown on errors
    - _Requirements: 1.9, 13.0, 10.0_

  - [~] 19.6 Test performance and optimization
    - Verify inference latency under 50ms
    - Verify frame rate at 30 FPS
    - Verify memory usage under 500MB
    - Verify GPU acceleration if available
    - _Requirements: 17.0, 17.1, 17.2, 17.3_

- [~] 20. Final Checkpoint - Production Ready
  - Ensure all tests pass
  - Verify documentation is complete
  - Verify installer works correctly
  - Verify application meets all requirements
  - Ask the user if questions arise before release

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP delivery
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation of functionality
- Backend implementation uses Python with FastAPI, TensorFlow, and OpenCV
- Frontend implementation uses React with TypeScript and Tailwind CSS
- Desktop wrapper uses Electron for native Windows integration
- All code should follow PEP 8 style guide for Python and ESLint rules for TypeScript
- Thread safety is critical for concurrent access to shared state
- Performance targets: 30 FPS, <50ms inference latency, <500MB memory

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1", "1.2", "1.3", "1.4"] },
    { "id": 1, "tasks": ["2.1", "2.2", "2.3", "3.1", "4.1", "5.1"] },
    { "id": 2, "tasks": ["2.4", "2.5", "2.6", "3.2", "3.3", "4.2", "4.3", "4.4", "5.2", "5.3"] },
    { "id": 3, "tasks": ["5.4", "5.5", "5.6", "5.7", "6.1", "6.2"] },
    { "id": 4, "tasks": ["6.3", "6.4", "6.5", "6.6", "6.7", "7.1"] },
    { "id": 5, "tasks": ["7.2", "7.3", "7.4", "8.1", "8.2"] },
    { "id": 6, "tasks": ["8.3", "8.4", "9.1", "9.2", "9.3", "9.4"] },
    { "id": 7, "tasks": ["10.1", "10.2", "10.3", "10.4", "11.1", "11.2", "11.3", "11.4"] },
    { "id": 8, "tasks": ["12.1", "12.2", "12.3", "12.4", "12.5"] },
    { "id": 9, "tasks": ["13.1", "13.2", "13.3", "13.4", "13.5"] },
    { "id": 10, "tasks": ["14.1", "14.2", "14.3", "14.4", "14.5", "14.6", "14.7", "14.8", "14.9", "14.10"] },
    { "id": 11, "tasks": ["16.1", "16.2", "16.3", "16.4"] },
    { "id": 12, "tasks": ["17.1", "17.2", "17.3", "17.4"] },
    { "id": 13, "tasks": ["18.1", "18.2", "18.3", "18.4"] },
    { "id": 14, "tasks": ["19.1", "19.2", "19.3", "19.4", "19.5", "19.6"] }
  ]
}
```
