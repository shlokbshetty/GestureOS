"""
Unit tests for GestureOS main entry point and orchestrator.
"""

from unittest.mock import MagicMock, patch
import pytest

from backend.main import GestureOSApplication, MockGestureEngine, parse_args


def test_mock_gesture_engine():
    engine = MockGestureEngine()
    assert engine.running is False
    assert engine.start() is True
    assert engine.running is True
    engine.stop()
    assert engine.running is False


def test_gesture_os_app_initialization():
    app = GestureOSApplication(
        config_path="config.json",
        model_path="non_existent_model.h5",
        host="127.0.0.1",
        port=5000,
        mock_engine=True,
    )
    app.initialize()
    
    assert app.config_manager is not None
    assert app.registry is not None
    assert app.controller is not None
    assert app.engine is not None
    assert app.state_manager is not None
    assert app.api_server is not None
    
    # Verify callbacks are wired
    assert len(app.engine.event_callbacks) >= 1
    assert len(app.state_manager.state_callbacks) >= 1
    assert len(app.controller.action_callbacks) >= 1
    
    # Test shutdown
    app.shutdown()
    assert app.shutdown_event.is_set()


def test_parse_args():
    with patch("sys.argv", ["main.py", "--host", "0.0.0.0", "--port", "8080", "--mock"]):
        args = parse_args()
        assert args.host == "0.0.0.0"
        assert args.port == 8080
        assert args.mock is True
