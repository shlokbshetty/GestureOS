"""
Application Main Entry Point for GestureOS.

Initializes and coordinates:
- Structured logging system
- Configuration manager and gesture registry
- Windows controller automation
- Gesture engine vision pipeline
- State manager lifecycle tracking
- FastAPI REST API & WebSocket server
- Graceful shutdown signal handling

Requirements: 7.0, 10.0, 13.0, 15.1, 15.2, 15.3
"""

import argparse
import os
import signal
import sys
import threading
import time
from pathlib import Path
from typing import Optional

# Ensure project root and backend are in python path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "backend"))

from backend.utils.logger import get_logger, initialize_logging, shutdown_logging
from backend.utils.config import ConfigManager
from backend.gesture_registry import GestureRegistry
from backend.controller import WindowsController
from backend.state_manager import StateManager
from backend.api_server import APIServer


class MockGestureEngine:
    """Fallback engine used when model file is not present or for dev/test mode."""
    
    def __init__(self, logger=None):
        self.logger = logger or get_logger("mock_gesture_engine")
        self.confidence_threshold = 0.70
        self.smoothing_frames = 20
        self.running = False
        self.camera = None
        self.fps_target = 30
        self.inference_latency = 0.0
        self.frame_count = 0
        self.event_callbacks = []
    
    def start(self) -> bool:
        self.running = True
        self.logger.info("MockGestureEngine started")
        return True
    
    def stop(self) -> None:
        self.running = False
        self.logger.info("MockGestureEngine stopped")
    
    def register_callback(self, callback) -> None:
        self.event_callbacks.append(callback)
    
    def get_frame_count(self) -> int:
        return self.frame_count


class GestureOSApplication:
    """
    Main application orchestrator managing lifecycle and component wiring.
    """
    
    def __init__(
        self,
        config_path: str = "config.json",
        model_path: Optional[str] = None,
        host: str = "127.0.0.1",
        port: int = 5000,
        mock_engine: bool = False,
    ):
        self.config_path = config_path
        self.model_path = model_path or "models/cnn_model_keras.h5"
        self.host = host
        self.port = port
        self.mock_engine = mock_engine
        
        # Shutdown event
        self.shutdown_event = threading.Event()
        self.logger = get_logger("main")
        
        # Components to be wired
        self.config_manager = None
        self.registry = None
        self.controller = None
        self.engine = None
        self.state_manager = None
        self.api_server = None
    
    def initialize(self) -> None:
        """Initialize all subsystems and wire event callbacks."""
        self.logger.info("Initializing GestureOS components...")
        
        # 1. Config Manager & Registry
        self.config_manager = ConfigManager(self.config_path)
        self.registry = GestureRegistry(self.config_path)
        
        # 2. Windows Controller
        self.controller = WindowsController(logger_instance=get_logger("controller"))
        
        # 3. Vision Engine (Load CNN or Fallback to Mock)
        resolved_model_path = Path(self.model_path)
        if not resolved_model_path.is_absolute():
            resolved_model_path = ROOT_DIR / self.model_path
        
        if self.mock_engine or not resolved_model_path.exists():
            if not self.mock_engine:
                self.logger.warning(
                    f"Model file not found at {resolved_model_path}. "
                    "Running in mock engine mode for UI and API connectivity."
                )
            self.engine = MockGestureEngine(logger=get_logger("mock_engine"))
        else:
            from backend.engine import GestureEngine
            self.engine = GestureEngine(
                model_path=str(resolved_model_path),
                confidence_threshold=self.config_manager.get("engine.confidence_threshold", 0.70),
                smoothing_frames=self.config_manager.get("engine.smoothing_frames", 20),
                logger=get_logger("gesture_engine"),
            )
        
        # 4. State Manager
        self.state_manager = StateManager(
            engine=self.engine,
            controller=self.controller,
            registry=self.registry,
            logger=get_logger("state_manager"),
        )
        
        # 5. API Server
        self.api_server = APIServer(
            state_manager=self.state_manager,
            engine=self.engine,
            registry=self.registry,
            logger=get_logger("api_server"),
            host=self.host,
            port=self.port,
        )
        
        # 6. Wire Event Callbacks
        self.engine.register_callback(self.state_manager.on_gesture_detected)
        self.engine.register_callback(
            lambda event_type, data: self.api_server.broadcast_event(event_type, data)
        )
        self.state_manager.register_callback(
            lambda event_type, data: self.api_server.broadcast_event(event_type, data)
        )
        self.controller.register_callback(
            lambda event_type, data: self.api_server.broadcast_event(event_type, data)
        )
        
        self.logger.info("GestureOS components initialized and wired successfully")
    
    def setup_signal_handlers(self) -> None:
        """Register signal handlers for graceful shutdown."""
        def _handler(signum, frame):
            sig_name = signal.Signals(signum).name
            self.logger.info(f"Received signal {sig_name}. Initiating graceful shutdown...")
            self.shutdown()
        
        try:
            signal.signal(signal.SIGINT, _handler)
            signal.signal(signal.SIGTERM, _handler)
        except (ValueError, AttributeError):
            pass
    
    def run(self) -> None:
        """Run the application and start serving API requests."""
        self.initialize()
        self.setup_signal_handlers()
        
        self.logger.info(f"API server listening on http://{self.host}:{self.port}")
        # Signal to Electron desktop wrapper that backend is ready
        print("API server started", flush=True)
        
        try:
            self.api_server.run()
        except KeyboardInterrupt:
            self.logger.info("Keyboard interrupt received")
        finally:
            self.shutdown()
    
    def shutdown(self) -> None:
        """Execute graceful shutdown sequence."""
        if self.shutdown_event.is_set():
            return
        self.shutdown_event.set()
        
        self.logger.info("Shutting down GestureOS...")
        
        # 1. Stop gesture recognition
        if self.state_manager:
            try:
                self.state_manager.stop()
            except Exception as e:
                self.logger.error(f"Error stopping state manager: {e}")
        
        # 2. Stop engine
        if self.engine:
            try:
                self.engine.stop()
            except Exception as e:
                self.logger.error(f"Error stopping vision engine: {e}")
        
        # 3. Shutdown API server
        if self.api_server:
            try:
                self.api_server.shutdown()
            except Exception as e:
                self.logger.error(f"Error stopping API server: {e}")
        
        # 4. Flush and close logs
        shutdown_logging()
        self.logger.info("GestureOS shutdown complete.")


def parse_args():
    parser = argparse.ArgumentParser(description="GestureOS Backend Service")
    parser.add_argument("--host", default="127.0.0.1", help="Host interface to bind (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=5000, help="Port to bind (default: 5000)")
    parser.add_argument("--config", default="config.json", help="Path to config.json (default: config.json)")
    parser.add_argument("--model", default="models/cnn_model_keras.h5", help="Path to CNN model file")
    parser.add_argument("--mock", action="store_true", help="Run with mock vision engine without webcam/model")
    return parser.parse_args()


def main():
    initialize_logging()
    args = parse_args()
    
    app = GestureOSApplication(
        config_path=args.config,
        model_path=args.model,
        host=args.host,
        port=args.port,
        mock_engine=args.mock,
    )
    app.run()


if __name__ == "__main__":
    main()
