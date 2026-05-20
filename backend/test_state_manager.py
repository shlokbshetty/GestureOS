"""
Unit tests for StateManager.

Tests cover:
- State transitions (stopped -> starting -> running -> pausing -> paused -> running -> stopping -> stopped)
- State validation (invalid transitions are rejected)
- Gesture detection event handling
- Cooldown tracking and expiry
- Action logging
- Thread-safe state access
- Event callbacks
- Status reporting
"""

import pytest
import threading
import time
import logging
from unittest.mock import Mock, MagicMock, patch, call
from collections import deque

from state_manager import StateManager, ApplicationState


class MockEngine:
    """Mock GestureEngine for testing."""
    def __init__(self):
        self.running = False
        self.started = False
        self.stopped = False
    
    def start(self):
        self.started = True
        self.running = True
        return True
    
    def stop(self):
        self.stopped = True
        self.running = False


class MockController:
    """Mock WindowsController for testing."""
    def __init__(self):
        self.executed_actions = []
    
    def execute_action(self, action_type, params=None):
        self.executed_actions.append({'action': action_type, 'params': params})
        return True


class MockRegistry:
    """Mock GestureRegistry for testing."""
    def __init__(self):
        self.gestures = {
            'app_switch': {
                'action': 'keyboard_shortcut',
                'params': {'keys': ['alt', 'tab']},
                'cooldown_ms': 500,
                'enabled': True
            },
            'close_window': {
                'action': 'keyboard_shortcut',
                'params': {'keys': ['alt', 'F4']},
                'cooldown_ms': 500,
                'enabled': True
            },
            'nothing': {
                'action': 'none',
                'params': {},
                'cooldown_ms': 0,
                'enabled': True
            }
        }
    
    def get_action(self, gesture_name):
        gesture = self.gestures.get(gesture_name)
        if gesture and gesture.get('enabled'):
            return {
                'action': gesture['action'],
                'params': gesture['params'],
                'cooldown_ms': gesture['cooldown_ms']
            }
        return None


class TestStateManagerInitialization:
    """Test StateManager initialization."""
    
    def test_initialization(self):
        """Test StateManager initialization."""
        engine = MockEngine()
        controller = MockController()
        registry = MockRegistry()
        logger = logging.getLogger('test')
        
        manager = StateManager(engine, controller, registry, logger)
        
        assert manager.state == ApplicationState.STOPPED
        assert manager.current_gesture == 'nothing'
        assert manager.last_action is None
        assert manager.start_time is None
        assert len(manager.action_log) == 0
        assert len(manager.cooldown_tracker) == 0
    
    def test_initialization_without_logger(self):
        """Test StateManager initialization without explicit logger."""
        engine = MockEngine()
        controller = MockController()
        registry = MockRegistry()
        
        manager = StateManager(engine, controller, registry)
        
        assert manager.logger is not None
        assert manager.state == ApplicationState.STOPPED


class TestStateTransitions:
    """Test state machine transitions."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.engine = MockEngine()
        self.controller = MockController()
        self.registry = MockRegistry()
        self.logger = logging.getLogger('test')
        self.manager = StateManager(self.engine, self.controller, self.registry, self.logger)
    
    def test_start_from_stopped(self):
        """Test starting from stopped state."""
        assert self.manager.start() is True
        assert self.manager.state == ApplicationState.RUNNING
        assert self.engine.started is True
        assert self.manager.start_time is not None
    
    def test_start_from_running_fails(self):
        """Test that starting from running state fails."""
        self.manager.start()
        assert self.manager.start() is False
        assert self.manager.state == ApplicationState.RUNNING
    
    def test_stop_from_running(self):
        """Test stopping from running state."""
        self.manager.start()
        assert self.manager.stop() is True
        assert self.manager.state == ApplicationState.STOPPED
        assert self.engine.stopped is True
    
    def test_stop_from_stopped_succeeds(self):
        """Test that stopping from stopped state succeeds (idempotent)."""
        assert self.manager.stop() is True
        assert self.manager.state == ApplicationState.STOPPED
    
    def test_pause_from_running(self):
        """Test pausing from running state."""
        self.manager.start()
        assert self.manager.pause() is True
        assert self.manager.state == ApplicationState.PAUSED
        assert self.engine.running is False
    
    def test_pause_from_stopped_fails(self):
        """Test that pausing from stopped state fails."""
        assert self.manager.pause() is False
        assert self.manager.state == ApplicationState.STOPPED
    
    def test_resume_from_paused(self):
        """Test resuming from paused state."""
        self.manager.start()
        self.manager.pause()
        assert self.manager.resume() is True
        assert self.manager.state == ApplicationState.RUNNING
        assert self.engine.running is True
    
    def test_resume_from_running_fails(self):
        """Test that resuming from running state fails."""
        self.manager.start()
        assert self.manager.resume() is False
        assert self.manager.state == ApplicationState.RUNNING
    
    def test_full_lifecycle(self):
        """Test complete state machine lifecycle."""
        # stopped -> starting -> running
        assert self.manager.start() is True
        assert self.manager.state == ApplicationState.RUNNING
        
        # running -> pausing -> paused
        assert self.manager.pause() is True
        assert self.manager.state == ApplicationState.PAUSED
        
        # paused -> running
        assert self.manager.resume() is True
        assert self.manager.state == ApplicationState.RUNNING
        
        # running -> stopping -> stopped
        assert self.manager.stop() is True
        assert self.manager.state == ApplicationState.STOPPED


class TestGestureDetectionHandling:
    """Test gesture detection event handling."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.engine = MockEngine()
        self.controller = MockController()
        self.registry = MockRegistry()
        self.logger = logging.getLogger('test')
        self.manager = StateManager(self.engine, self.controller, self.registry, self.logger)
    
    def test_gesture_ignored_when_stopped(self):
        """Test that gestures are ignored when application is stopped."""
        self.manager.on_gesture_detected('app_switch', 0.95)
        
        assert len(self.controller.executed_actions) == 0
        assert len(self.manager.action_log) == 0
    
    def test_gesture_ignored_when_paused(self):
        """Test that gestures are ignored when application is paused."""
        self.manager.start()
        self.manager.pause()
        
        self.manager.on_gesture_detected('app_switch', 0.95)
        
        assert len(self.controller.executed_actions) == 0
        assert len(self.manager.action_log) == 0
    
    def test_gesture_executed_when_running(self):
        """Test that gestures are executed when application is running."""
        self.manager.start()
        
        self.manager.on_gesture_detected('app_switch', 0.95)
        
        assert len(self.controller.executed_actions) == 1
        assert self.controller.executed_actions[0]['action'] == 'keyboard_shortcut'
        assert len(self.manager.action_log) == 1
    
    def test_gesture_updates_current_gesture(self):
        """Test that detected gesture updates current_gesture."""
        self.manager.start()
        
        self.manager.on_gesture_detected('app_switch', 0.95)
        assert self.manager.current_gesture == 'app_switch'
        
        self.manager.on_gesture_detected('close_window', 0.90)
        assert self.manager.current_gesture == 'close_window'
    
    def test_nothing_gesture_not_executed(self):
        """Test that 'nothing' gesture doesn't execute action."""
        self.manager.start()
        
        self.manager.on_gesture_detected('nothing', 0.95)
        
        assert len(self.controller.executed_actions) == 0
        assert len(self.manager.action_log) == 0
    
    def test_disabled_gesture_not_executed(self):
        """Test that disabled gestures don't execute."""
        self.manager.start()
        self.registry.gestures['app_switch']['enabled'] = False
        
        self.manager.on_gesture_detected('app_switch', 0.95)
        
        assert len(self.controller.executed_actions) == 0
        assert len(self.manager.action_log) == 0


class TestCooldownTracking:
    """Test cooldown period tracking."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.engine = MockEngine()
        self.controller = MockController()
        self.registry = MockRegistry()
        self.logger = logging.getLogger('test')
        self.manager = StateManager(self.engine, self.controller, self.registry, self.logger)
    
    def test_cooldown_prevents_rapid_execution(self):
        """Test that cooldown prevents rapid gesture re-triggering."""
        self.manager.start()
        
        # First gesture should execute
        self.manager.on_gesture_detected('app_switch', 0.95)
        assert len(self.controller.executed_actions) == 1
        
        # Second gesture immediately should be blocked by cooldown
        self.manager.on_gesture_detected('app_switch', 0.95)
        assert len(self.controller.executed_actions) == 1  # Still 1, not 2
    
    def test_cooldown_expires(self):
        """Test that cooldown expires after specified time."""
        self.manager.start()
        
        # First gesture
        self.manager.on_gesture_detected('app_switch', 0.95)
        assert len(self.controller.executed_actions) == 1
        
        # Wait for cooldown to expire (500ms + buffer)
        time.sleep(0.6)
        
        # Second gesture should execute after cooldown expires
        self.manager.on_gesture_detected('app_switch', 0.95)
        assert len(self.controller.executed_actions) == 2
    
    def test_different_gestures_not_blocked_by_cooldown(self):
        """Test that different gestures are not blocked by each other's cooldown."""
        self.manager.start()
        
        # First gesture
        self.manager.on_gesture_detected('app_switch', 0.95)
        assert len(self.controller.executed_actions) == 1
        
        # Different gesture should execute immediately
        self.manager.on_gesture_detected('close_window', 0.95)
        assert len(self.controller.executed_actions) == 2
    
    def test_gesture_with_zero_cooldown(self):
        """Test that gestures with zero cooldown execute immediately."""
        self.manager.start()
        self.registry.gestures['nothing']['cooldown_ms'] = 0
        
        # Multiple executions should work without cooldown
        self.manager.on_gesture_detected('nothing', 0.95)
        self.manager.on_gesture_detected('nothing', 0.95)
        
        # 'nothing' doesn't execute actions, so check cooldown tracker
        assert 'nothing' not in self.manager.cooldown_tracker


class TestActionLogging:
    """Test action logging functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.engine = MockEngine()
        self.controller = MockController()
        self.registry = MockRegistry()
        self.logger = logging.getLogger('test')
        self.manager = StateManager(self.engine, self.controller, self.registry, self.logger)
    
    def test_action_logged_on_execution(self):
        """Test that actions are logged when executed."""
        self.manager.start()
        
        self.manager.on_gesture_detected('app_switch', 0.95)
        
        assert len(self.manager.action_log) == 1
        action = self.manager.action_log[0]
        assert action['gesture'] == 'app_switch'
        assert action['action'] == 'keyboard_shortcut'
        assert action['confidence'] == 0.95
        assert action['success'] is True
    
    def test_action_log_max_size(self):
        """Test that action log respects max size (1000 entries)."""
        self.manager.start()
        
        # Add more than 1000 actions
        for i in range(1100):
            self.manager.on_gesture_detected('app_switch', 0.95)
            time.sleep(0.001)  # Small delay to avoid cooldown
        
        # Log should only contain last 1000
        assert len(self.manager.action_log) == 1000
    
    def test_get_action_log(self):
        """Test retrieving action log with limit."""
        self.manager.start()
        
        # Add 5 actions
        for i in range(5):
            self.manager.on_gesture_detected('app_switch', 0.95)
            time.sleep(0.6)  # Wait for cooldown
        
        # Get last 3 actions
        log = self.manager.get_action_log(limit=3)
        assert len(log) == 3
        # Most recent should be first
        assert log[0]['gesture'] == 'app_switch'
    
    def test_clear_action_log(self):
        """Test clearing action log."""
        self.manager.start()
        
        self.manager.on_gesture_detected('app_switch', 0.95)
        assert len(self.manager.action_log) > 0
        
        self.manager.clear_action_log()
        assert len(self.manager.action_log) == 0


class TestEventCallbacks:
    """Test event callback system."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.engine = MockEngine()
        self.controller = MockController()
        self.registry = MockRegistry()
        self.logger = logging.getLogger('test')
        self.manager = StateManager(self.engine, self.controller, self.registry, self.logger)
        self.events = []
    
    def callback(self, event_type, data):
        """Test callback that records events."""
        self.events.append({'type': event_type, 'data': data})
    
    def test_state_changed_event_emitted(self):
        """Test that state_changed event is emitted on transitions."""
        self.manager.register_callback(self.callback)
        
        self.manager.start()
        
        # Should have events for: starting, running
        state_events = [e for e in self.events if e['type'] == 'state_changed']
        assert len(state_events) >= 2
        assert state_events[0]['data']['new_state'] == 'starting'
        assert state_events[1]['data']['new_state'] == 'running'
    
    def test_callback_registration_and_unregistration(self):
        """Test callback registration and unregistration."""
        self.manager.register_callback(self.callback)
        self.manager.start()
        
        events_before = len(self.events)
        
        self.manager.unregister_callback(self.callback)
        self.manager.stop()
        
        # No new events should be recorded after unregistration
        events_after = len(self.events)
        assert events_after == events_before
    
    def test_callback_exception_handling(self):
        """Test that exceptions in callbacks don't crash the manager."""
        def bad_callback(event_type, data):
            raise Exception("Test exception")
        
        self.manager.register_callback(bad_callback)
        self.manager.register_callback(self.callback)
        
        # Should not raise exception
        self.manager.start()
        
        # Good callback should still be called
        assert len(self.events) > 0


class TestThreadSafety:
    """Test thread-safe state access."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.engine = MockEngine()
        self.controller = MockController()
        self.registry = MockRegistry()
        self.logger = logging.getLogger('test')
        self.manager = StateManager(self.engine, self.controller, self.registry, self.logger)
    
    def test_concurrent_gesture_detection(self):
        """Test that concurrent gesture detection is thread-safe."""
        self.manager.start()
        
        def detect_gestures():
            for i in range(10):
                self.manager.on_gesture_detected('app_switch', 0.95)
                time.sleep(0.01)
        
        threads = [threading.Thread(target=detect_gestures) for _ in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # All actions should be logged without corruption
        assert len(self.manager.action_log) > 0
    
    def test_concurrent_state_transitions(self):
        """Test that concurrent state transitions are handled safely."""
        self.manager.start()
        
        def toggle_pause():
            for i in range(5):
                if self.manager.is_running():
                    self.manager.pause()
                    time.sleep(0.01)
                if self.manager.is_paused():
                    self.manager.resume()
                    time.sleep(0.01)
        
        thread = threading.Thread(target=toggle_pause)
        thread.start()
        thread.join()
        
        # Should end in a valid state
        assert self.manager.state in [ApplicationState.RUNNING, ApplicationState.PAUSED]


class TestStatusReporting:
    """Test status reporting methods."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.engine = MockEngine()
        self.controller = MockController()
        self.registry = MockRegistry()
        self.logger = logging.getLogger('test')
        self.manager = StateManager(self.engine, self.controller, self.registry, self.logger)
    
    def test_get_state(self):
        """Test getting current state."""
        assert self.manager.get_state() == 'stopped'
        
        self.manager.start()
        assert self.manager.get_state() == 'running'
        
        self.manager.pause()
        assert self.manager.get_state() == 'paused'
    
    def test_get_status(self):
        """Test getting comprehensive status."""
        self.manager.start()
        
        status = self.manager.get_status()
        
        assert status['state'] == 'running'
        assert status['current_gesture'] == 'nothing'
        assert status['uptime_seconds'] > 0
        assert 'timestamp' in status
    
    def test_is_running(self):
        """Test is_running method."""
        assert self.manager.is_running() is False
        
        self.manager.start()
        assert self.manager.is_running() is True
        
        self.manager.pause()
        assert self.manager.is_running() is False
    
    def test_is_paused(self):
        """Test is_paused method."""
        assert self.manager.is_paused() is False
        
        self.manager.start()
        assert self.manager.is_paused() is False
        
        self.manager.pause()
        assert self.manager.is_paused() is True
    
    def test_is_stopped(self):
        """Test is_stopped method."""
        assert self.manager.is_stopped() is True
        
        self.manager.start()
        assert self.manager.is_stopped() is False
        
        self.manager.stop()
        assert self.manager.is_stopped() is True
    
    def test_get_cooldown_status(self):
        """Test getting cooldown status."""
        self.manager.start()
        
        # No cooldowns initially
        assert len(self.manager.get_cooldown_status()) == 0
        
        # Execute gesture to set cooldown
        self.manager.on_gesture_detected('app_switch', 0.95)
        
        cooldown_status = self.manager.get_cooldown_status()
        assert 'app_switch' in cooldown_status
        assert cooldown_status['app_switch'] > 0


class TestStateConstants:
    """Test state constants for backward compatibility."""
    
    def test_state_constants_exist(self):
        """Test that state constants are defined."""
        assert StateManager.STATES['stopped'] == ApplicationState.STOPPED
        assert StateManager.STATES['starting'] == ApplicationState.STARTING
        assert StateManager.STATES['running'] == ApplicationState.RUNNING
        assert StateManager.STATES['pausing'] == ApplicationState.PAUSING
        assert StateManager.STATES['paused'] == ApplicationState.PAUSED
        assert StateManager.STATES['stopping'] == ApplicationState.STOPPING


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
