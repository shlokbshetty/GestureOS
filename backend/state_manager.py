"""
State Manager for Gesture Control Desktop Application.

This module manages the application lifecycle and state transitions.
It tracks the current state, gestures, and cooldown periods, and emits
state change events for other components to react to.

Requirements: 4.1, 4.2, 4.6
"""

import threading
import time
from collections import deque
from typing import Callable, Dict, Optional, List
from enum import Enum
import logging


class ApplicationState(Enum):
    """
    Application state enumeration.
    
    State Machine:
        STOPPED -> STARTING -> RUNNING
                              ↓
                            PAUSING -> PAUSED
                              ↑
                            RESUMING
                              ↓
                            STOPPING -> STOPPED
    """
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    PAUSING = "pausing"
    PAUSED = "paused"
    STOPPING = "stopping"


class StateManager:
    """
    Manage application lifecycle and state transitions.
    
    Responsibilities:
    - Maintain application state machine
    - Track current gesture and last action
    - Manage cooldown periods per gesture
    - Emit state change events
    - Handle graceful shutdown
    - Provide thread-safe state access
    
    Attributes:
        state: Current application state
        current_gesture: Currently detected gesture
        last_action: Last executed action
        last_action_time: Timestamp of last action
        start_time: Application start timestamp
        action_log: Deque of recent actions (max 1000)
        cooldown_tracker: Dict mapping gesture names to cooldown expiry times
        lock: RLock for thread-safe state access
    """
    
    # State constants for backward compatibility
    STATES = {
        'stopped': ApplicationState.STOPPED,
        'starting': ApplicationState.STARTING,
        'running': ApplicationState.RUNNING,
        'pausing': ApplicationState.PAUSING,
        'paused': ApplicationState.PAUSED,
        'stopping': ApplicationState.STOPPING
    }
    
    def __init__(self, engine, controller, registry, logger: Optional[logging.Logger] = None):
        """
        Initialize StateManager.
        
        Args:
            engine: GestureEngine instance for gesture detection
            controller: WindowsController instance for action execution
            registry: GestureRegistry instance for gesture-to-action mapping
            logger: Logger instance (optional, will create if not provided)
        """
        self.engine = engine
        self.controller = controller
        self.registry = registry
        self.logger = logger or logging.getLogger(__name__)
        
        # State tracking
        self.state = ApplicationState.STOPPED
        self.current_gesture = 'nothing'
        self.last_action = None
        self.last_action_time = 0
        self.start_time = None
        
        # Action logging
        self.action_log = deque(maxlen=1000)
        
        # Cooldown tracking: gesture_name -> expiry_time
        self.cooldown_tracker = {}
        
        # Thread safety
        self.lock = threading.RLock()
        
        # Event callbacks
        self.state_callbacks = []
        
        self.logger.debug("StateManager initialized")
    
    def start(self) -> bool:
        """
        Start gesture recognition.
        
        Transitions: stopped -> starting -> running
        
        Returns:
            True if successful, False otherwise
        """
        with self.lock:
            if self.state != ApplicationState.STOPPED:
                self.logger.warning(
                    f"Cannot start from state: {self.state.value}. "
                    f"Current state must be 'stopped'"
                )
                return False
            
            # Transition to starting
            self._transition_state(ApplicationState.STARTING)
            
            # Initialize engine
            if not self.engine.start():
                self.logger.error("Failed to start gesture engine")
                self._transition_state(ApplicationState.STOPPED)
                return False
            
            # Record start time
            self.start_time = time.time()
            
            # Transition to running
            self._transition_state(ApplicationState.RUNNING)
            self.logger.info("Application started successfully")
            return True
    
    def stop(self) -> bool:
        """
        Stop gesture recognition.
        
        Transitions: running/paused -> stopping -> stopped
        
        Waits for in-flight actions to complete (max 5 seconds) before
        stopping the engine.
        
        Returns:
            True if successful, False otherwise
        """
        with self.lock:
            if self.state == ApplicationState.STOPPED:
                self.logger.debug("Application already stopped")
                return True
            
            if self.state not in [ApplicationState.RUNNING, ApplicationState.PAUSED]:
                self.logger.warning(
                    f"Cannot stop from state: {self.state.value}. "
                    f"Current state must be 'running' or 'paused'"
                )
                return False
            
            # Transition to stopping
            self._transition_state(ApplicationState.STOPPING)
            
            # Wait for in-flight actions (max 5 seconds)
            timeout = time.time() + 5
            while self.last_action_time > time.time() - 1 and time.time() < timeout:
                # Release lock while waiting to allow other threads to proceed
                self.lock.release()
                time.sleep(0.1)
                self.lock.acquire()
            
            # Stop engine
            self.engine.stop()
            
            # Transition to stopped
            self._transition_state(ApplicationState.STOPPED)
            self.logger.info("Application stopped successfully")
            return True
    
    def pause(self) -> bool:
        """
        Pause gesture detection.
        
        Transitions: running -> pausing -> paused
        
        The engine continues running but gesture detection is paused.
        
        Returns:
            True if successful, False otherwise
        """
        with self.lock:
            if self.state != ApplicationState.RUNNING:
                self.logger.warning(
                    f"Cannot pause from state: {self.state.value}. "
                    f"Current state must be 'running'"
                )
                return False
            
            # Transition to pausing
            self._transition_state(ApplicationState.PAUSING)
            
            # Pause engine
            self.engine.running = False
            
            # Transition to paused
            self._transition_state(ApplicationState.PAUSED)
            self.logger.info("Application paused successfully")
            return True
    
    def resume(self) -> bool:
        """
        Resume gesture detection.
        
        Transitions: paused -> running
        
        Returns:
            True if successful, False otherwise
        """
        with self.lock:
            if self.state != ApplicationState.PAUSED:
                self.logger.warning(
                    f"Cannot resume from state: {self.state.value}. "
                    f"Current state must be 'paused'"
                )
                return False
            
            # Resume engine
            self.engine.running = True
            
            # Transition to running
            self._transition_state(ApplicationState.RUNNING)
            self.logger.info("Application resumed successfully")
            return True
    
    def on_gesture_detected(self, gesture: str, confidence: float) -> None:
        """
        Handle gesture detection event from engine.
        
        This method is called when the engine detects a gesture.
        It checks cooldown, looks up the action, executes it, and logs it.
        
        Args:
            gesture: Detected gesture name
            confidence: Detection confidence (0.0-1.0)
        """
        with self.lock:
            if self.state != ApplicationState.RUNNING:
                self.logger.debug(
                    f"Ignoring gesture '{gesture}' - application not running "
                    f"(state: {self.state.value})"
                )
                return
            
            # Update current gesture
            self.current_gesture = gesture
            
            # Check cooldown
            if not self._check_cooldown(gesture):
                self.logger.debug(
                    f"Gesture '{gesture}' ignored - cooldown active"
                )
                return
            
            # Get action from registry
            action_info = self.registry.get_action(gesture)
            if not action_info:
                self.logger.debug(
                    f"No action configured for gesture '{gesture}' or gesture disabled"
                )
                return
            
            # Execute action
            success = self.controller.execute_action(
                action_info['action'],
                action_info.get('params', {})
            )
            
            # Update last action time
            self.last_action_time = time.time()
            
            # Set cooldown for this gesture
            cooldown_ms = action_info.get('cooldown_ms', 0)
            if cooldown_ms > 0:
                self.cooldown_tracker[gesture] = time.time() + (cooldown_ms / 1000.0)
            
            # Log action
            action_entry = {
                'gesture': gesture,
                'action': action_info['action'],
                'confidence': confidence,
                'timestamp': self.last_action_time,
                'success': success
            }
            self.action_log.append(action_entry)
            self.last_action = action_entry
            
            if success:
                self.logger.info(
                    f"Action executed: {action_info['action']} "
                    f"(gesture: {gesture}, confidence: {confidence:.2f})"
                )
            else:
                self.logger.warning(
                    f"Action execution failed: {action_info['action']} "
                    f"(gesture: {gesture})"
                )
    
    def _check_cooldown(self, gesture: str) -> bool:
        """
        Check if gesture is in cooldown period.
        
        Args:
            gesture: Gesture name to check
        
        Returns:
            True if gesture is not in cooldown, False otherwise
        """
        if gesture not in self.cooldown_tracker:
            return True
        
        expiry_time = self.cooldown_tracker[gesture]
        if time.time() >= expiry_time:
            # Cooldown expired, remove from tracker
            del self.cooldown_tracker[gesture]
            return True
        
        return False
    
    def _transition_state(self, new_state: ApplicationState) -> None:
        """
        Transition to a new state and emit event.
        
        Args:
            new_state: New application state
        """
        old_state = self.state
        self.state = new_state
        
        self.logger.debug(
            f"State transition: {old_state.value} -> {new_state.value}"
        )
        
        # Emit state_changed event
        self._emit_event('state_changed', {
            'old_state': old_state.value,
            'new_state': new_state.value,
            'timestamp': time.time()
        })
    
    def _emit_event(self, event_type: str, data: Dict) -> None:
        """
        Emit event to registered callbacks.
        
        Args:
            event_type: Type of event
            data: Event data dictionary
        """
        for callback in self.state_callbacks:
            try:
                callback(event_type, data)
            except Exception as e:
                self.logger.error(
                    f"Error in state callback for event '{event_type}': {e}",
                    exc_info=True
                )
    
    def register_callback(self, callback: Callable) -> None:
        """
        Register callback for state change events.
        
        Callback signature: callback(event_type: str, data: dict)
        
        Args:
            callback: Callback function to register
        """
        with self.lock:
            self.state_callbacks.append(callback)
            self.logger.debug(f"State callback registered: {callback.__name__}")
    
    def unregister_callback(self, callback: Callable) -> None:
        """
        Unregister callback for state change events.
        
        Args:
            callback: Callback function to unregister
        """
        with self.lock:
            if callback in self.state_callbacks:
                self.state_callbacks.remove(callback)
                self.logger.debug(f"State callback unregistered: {callback.__name__}")
    
    def get_state(self) -> str:
        """
        Get current application state.
        
        Returns:
            Current state as string (e.g., 'running', 'stopped')
        """
        with self.lock:
            return self.state.value
    
    def get_status(self) -> Dict:
        """
        Get comprehensive application status.
        
        Returns:
            Dictionary with current state, gesture, uptime, and metrics
        """
        with self.lock:
            uptime = 0
            if self.start_time:
                uptime = time.time() - self.start_time
            
            return {
                'state': self.state.value,
                'current_gesture': self.current_gesture,
                'last_action': self.last_action,
                'uptime_seconds': uptime,
                'total_actions': len(self.action_log),
                'timestamp': time.time()
            }
    
    def get_action_log(self, limit: int = 100) -> List[Dict]:
        """
        Get recent action log entries.
        
        Args:
            limit: Maximum number of entries to return (default 100)
        
        Returns:
            List of action log entries (most recent first)
        """
        with self.lock:
            # Convert deque to list and reverse to get most recent first
            log_list = list(self.action_log)
            log_list.reverse()
            return log_list[:limit]
    
    def clear_action_log(self) -> None:
        """Clear the action log."""
        with self.lock:
            self.action_log.clear()
            self.logger.debug("Action log cleared")
    
    def get_cooldown_status(self) -> Dict[str, float]:
        """
        Get current cooldown status for all gestures.
        
        Returns:
            Dictionary mapping gesture names to remaining cooldown time in seconds
        """
        with self.lock:
            current_time = time.time()
            cooldown_status = {}
            
            for gesture, expiry_time in self.cooldown_tracker.items():
                remaining = expiry_time - current_time
                if remaining > 0:
                    cooldown_status[gesture] = remaining
            
            return cooldown_status
    
    def is_running(self) -> bool:
        """
        Check if application is currently running.
        
        Returns:
            True if state is RUNNING, False otherwise
        """
        with self.lock:
            return self.state == ApplicationState.RUNNING
    
    def is_paused(self) -> bool:
        """
        Check if application is currently paused.
        
        Returns:
            True if state is PAUSED, False otherwise
        """
        with self.lock:
            return self.state == ApplicationState.PAUSED
    
    def is_stopped(self) -> bool:
        """
        Check if application is currently stopped.
        
        Returns:
            True if state is STOPPED, False otherwise
        """
        with self.lock:
            return self.state == ApplicationState.STOPPED
