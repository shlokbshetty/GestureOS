"""
Unit tests for Debouncer and CooldownTracker.
"""

import time
import pytest
from backend.utils.debounce import Debouncer, CooldownTracker


def test_debouncer_basic():
    debouncer = Debouncer(window_ms=100)
    
    # First call should succeed
    assert debouncer.should_process() is True
    
    # Immediate call within window should be rejected
    assert debouncer.should_process() is False
    
    # After waiting beyond window, should succeed
    time.sleep(0.12)
    assert debouncer.should_process() is True


def test_debouncer_reset():
    debouncer = Debouncer(window_ms=500)
    assert debouncer.should_process() is True
    assert debouncer.should_process() is False
    
    debouncer.reset()
    assert debouncer.should_process() is True


def test_cooldown_tracker():
    tracker = CooldownTracker()
    
    assert tracker.is_in_cooldown("volume_up") is False
    assert tracker.get_remaining_ms("volume_up") == 0
    
    # Set cooldown of 150ms
    tracker.set_cooldown("volume_up", 150)
    assert tracker.is_in_cooldown("volume_up") is True
    assert tracker.get_remaining_ms("volume_up") > 0
    
    # Other gestures should not be in cooldown
    assert tracker.is_in_cooldown("volume_down") is False
    
    # Wait for cooldown to expire
    time.sleep(0.18)
    assert tracker.is_in_cooldown("volume_up") is False
    assert tracker.get_remaining_ms("volume_up") == 0


def test_cooldown_tracker_clear():
    tracker = CooldownTracker()
    tracker.set_cooldown("gesture1", 5000)
    tracker.set_cooldown("gesture2", 5000)
    
    assert tracker.is_in_cooldown("gesture1") is True
    assert tracker.is_in_cooldown("gesture2") is True
    
    tracker.clear("gesture1")
    assert tracker.is_in_cooldown("gesture1") is False
    assert tracker.is_in_cooldown("gesture2") is True
    
    tracker.clear()
    assert tracker.is_in_cooldown("gesture2") is False
