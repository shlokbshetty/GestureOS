"""
Unit tests for TemporalSmoother.
"""

import pytest
from backend.utils.smoothing import TemporalSmoother


def test_smoothing_confirmation():
    smoother = TemporalSmoother(smoothing_frames=5, min_confidence=0.7)
    
    # 4 frames - not enough
    for _ in range(4):
        result = smoother.add_prediction("volume_up", 0.9)
        assert result is None
    
    # 5th frame - confirmed!
    result = smoother.add_prediction("volume_up", 0.9)
    assert result is not None
    assert result["gesture"] == "volume_up"
    assert pytest.approx(result["confidence"], 0.01) == 0.9
    assert result["frames"] == 5
    
    # Buffer should be reset after confirmation
    assert len(smoother.get_buffer()) == 0


def test_smoothing_ignores_nothing():
    smoother = TemporalSmoother(smoothing_frames=3, min_confidence=0.5)
    
    for _ in range(5):
        result = smoother.add_prediction("nothing", 0.95)
        assert result is None


def test_smoothing_low_confidence():
    smoother = TemporalSmoother(smoothing_frames=3, min_confidence=0.8)
    
    # Average confidence 0.6 is below 0.8
    assert smoother.add_prediction("scroll_up", 0.6) is None
    assert smoother.add_prediction("scroll_up", 0.6) is None
    assert smoother.add_prediction("scroll_up", 0.6) is None


def test_smoothing_mixed_gestures():
    smoother = TemporalSmoother(smoothing_frames=3, min_confidence=0.7)
    
    smoother.add_prediction("volume_up", 0.9)
    smoother.add_prediction("volume_down", 0.9)
    smoother.add_prediction("volume_up", 0.9)
    # Mixed gestures should not confirm
    assert smoother.add_prediction("volume_up", 0.9) is None
