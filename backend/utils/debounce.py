"""
Debounce and Cooldown System

Provides debouncing for rapid events and cooldown tracking per gesture
to prevent unintentional repeated triggering of actions.

Requirements: 7.0, 3.11
"""

import time
import threading
from typing import Dict, Optional


class Debouncer:
    """
    Debounce rapid events within a time window.
    
    Algorithm:
    1. Track last event timestamp
    2. If new event occurs within window, ignore it
    3. If elapsed time >= window, process event and update timestamp
    """
    
    def __init__(self, window_ms: int = 500):
        """
        Initialize Debouncer.
        
        Args:
            window_ms: Minimum duration between allowed events in milliseconds.
        """
        self.window_ms = window_ms
        self.last_event_time = 0.0
        self.lock = threading.RLock()
    
    def should_process(self) -> bool:
        """
        Check if an event should be processed.
        
        Returns:
            True if enough time has elapsed since last event, False otherwise.
        """
        with self.lock:
            now = time.time() * 1000.0
            if now - self.last_event_time >= self.window_ms:
                self.last_event_time = now
                return True
            return False
    
    def reset(self) -> None:
        """Reset debounce timer."""
        with self.lock:
            self.last_event_time = 0.0


class CooldownTracker:
    """
    Track cooldown periods for multiple gestures.
    
    Prevents rapid re-triggering of the same gesture while allowing
    different gestures to proceed according to their independent cooldowns.
    """
    
    def __init__(self):
        """Initialize CooldownTracker."""
        self.cooldowns: Dict[str, float] = {}  # gesture -> expiry_timestamp (seconds)
        self.lock = threading.RLock()
    
    def set_cooldown(self, gesture: str, duration_ms: int) -> None:
        """
        Set a cooldown duration for a specific gesture.
        
        Args:
            gesture: The gesture name.
            duration_ms: Cooldown duration in milliseconds.
        """
        with self.lock:
            if duration_ms <= 0:
                self.cooldowns.pop(gesture, None)
                return
            self.cooldowns[gesture] = time.time() + (duration_ms / 1000.0)
    
    def is_in_cooldown(self, gesture: str) -> bool:
        """
        Check if a gesture is currently in cooldown.
        
        Args:
            gesture: The gesture name.
            
        Returns:
            True if in cooldown, False if ready.
        """
        with self.lock:
            if gesture not in self.cooldowns:
                return False
            
            now = time.time()
            if now >= self.cooldowns[gesture]:
                del self.cooldowns[gesture]
                return False
            
            return True
    
    def get_remaining_ms(self, gesture: str) -> int:
        """
        Get remaining cooldown time in milliseconds.
        
        Args:
            gesture: The gesture name.
            
        Returns:
            Remaining cooldown time in milliseconds (0 if not in cooldown).
        """
        with self.lock:
            if gesture not in self.cooldowns:
                return 0
            
            remaining = (self.cooldowns[gesture] - time.time()) * 1000.0
            if remaining <= 0:
                del self.cooldowns[gesture]
                return 0
            
            return int(remaining)
    
    def clear(self, gesture: Optional[str] = None) -> None:
        """
        Clear cooldowns.
        
        Args:
            gesture: Optional gesture name. If None, clears all cooldowns.
        """
        with self.lock:
            if gesture:
                self.cooldowns.pop(gesture, None)
            else:
                self.cooldowns.clear()
