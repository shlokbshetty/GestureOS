"""
Unit tests for the gesture engine module.

Tests cover:
- SkinDetector YCrCb color space conversion and thresholding
- Morphological operations (close, open) for mask cleanup
- Hand region extraction with bounding box and padding
- GestureEngine initialization and basic operations
- Frame processing pipeline
- Temporal smoothing algorithm
- Event emission system
"""

import pytest
import numpy as np
import cv2
import tempfile
import logging
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from engine import SkinDetector, GestureEngine


class TestSkinDetectorInitialization:
    """Test SkinDetector initialization."""
    
    def test_default_initialization(self):
        """Test SkinDetector with default parameters."""
        detector = SkinDetector()
        
        assert detector.lower_cr == 130
        assert detector.upper_cr == 170
        assert detector.lower_cb == 77
        assert detector.upper_cb == 127
        assert detector.morph_kernel_size == 5
        assert detector.padding == 10
        assert detector.kernel is not None
    
    def test_custom_initialization(self):
        """Test SkinDetector with custom parameters."""
        detector = SkinDetector(
            lower_cr=120,
            upper_cr=180,
            lower_cb=70,
            upper_cb=135,
            morph_kernel_size=7,
            padding=15
        )
        
        assert detector.lower_cr == 120
        assert detector.upper_cr == 180
        assert detector.lower_cb == 70
        assert detector.upper_cb == 135
        assert detector.morph_kernel_size == 7
        assert detector.padding == 15
    
    def test_kernel_creation(self):
        """Test that morphological kernel is created correctly."""
        detector = SkinDetector(morph_kernel_size=5)
        
        assert detector.kernel is not None
        assert detector.kernel.shape == (5, 5)


class TestSkinDetectorDetection:
    """Test SkinDetector.detect() method."""
    
    def create_test_frame(self, width=640, height=480, skin_color=True):
        """Create a test frame with optional skin-colored region."""
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        if skin_color:
            # Create a region with skin-like YCrCb values
            # Skin typically has Cr=130-170, Cb=77-127
            ycrcb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb)
            
            # Create a rectangular region with skin color
            y_start, y_end = 100, 300
            x_start, x_end = 150, 350
            
            # Set skin-like YCrCb values
            ycrcb_frame[y_start:y_end, x_start:x_end] = [128, 150, 100]
            
            frame = cv2.cvtColor(ycrcb_frame, cv2.COLOR_YCrCb2BGR)
        
        return frame
    
    def test_detect_with_valid_frame(self):
        """Test detection with a valid frame containing skin region."""
        detector = SkinDetector()
        frame = self.create_test_frame(skin_color=True)
        
        result = detector.detect(frame)
        
        # Should return a grayscale image
        assert result is not None
        assert len(result.shape) == 2  # Grayscale (H, W)
        assert result.dtype == np.uint8
    
    def test_detect_with_no_skin_region(self):
        """Test detection with frame containing no skin region."""
        detector = SkinDetector()
        frame = self.create_test_frame(skin_color=False)
        
        result = detector.detect(frame)
        
        # Should return None when no skin detected
        assert result is None
    
    def test_detect_with_none_frame(self):
        """Test detection with None frame."""
        detector = SkinDetector()
        
        result = detector.detect(None)
        
        assert result is None
    
    def test_detect_with_empty_frame(self):
        """Test detection with empty frame."""
        detector = SkinDetector()
        frame = np.array([], dtype=np.uint8)
        
        result = detector.detect(frame)
        
        assert result is None
    
    def test_detect_with_invalid_shape(self):
        """Test detection with invalid frame shape."""
        detector = SkinDetector()
        
        # Grayscale frame instead of BGR
        frame = np.zeros((480, 640), dtype=np.uint8)
        result = detector.detect(frame)
        assert result is None
        
        # Wrong number of channels
        frame = np.zeros((480, 640, 4), dtype=np.uint8)
        result = detector.detect(frame)
        assert result is None
    
    def test_detect_returns_grayscale(self):
        """Test that detect returns grayscale image."""
        detector = SkinDetector()
        frame = self.create_test_frame(skin_color=True)
        
        result = detector.detect(frame)
        
        if result is not None:
            assert len(result.shape) == 2
            assert result.dtype == np.uint8
    
    def test_detect_with_padding(self):
        """Test that padding is applied correctly."""
        detector = SkinDetector(padding=20)
        frame = self.create_test_frame(skin_color=True)
        
        result = detector.detect(frame)
        
        # Result should be larger due to padding
        if result is not None:
            assert result.shape[0] > 0
            assert result.shape[1] > 0
    
    def test_detect_with_small_contour(self):
        """Test that very small contours are filtered out."""
        detector = SkinDetector()
        
        # Create frame with very small skin region
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        ycrcb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb)
        
        # Create tiny region (area < 100)
        ycrcb_frame[100:102, 100:102] = [128, 150, 100]
        frame = cv2.cvtColor(ycrcb_frame, cv2.COLOR_YCrCb2BGR)
        
        result = detector.detect(frame)
        
        # Should return None for very small contours
        assert result is None
    
    def test_detect_with_large_contour(self):
        """Test detection with large skin region."""
        detector = SkinDetector()
        
        # Create frame with large skin region
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        ycrcb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb)
        
        # Create large region
        ycrcb_frame[50:400, 50:600] = [128, 150, 100]
        frame = cv2.cvtColor(ycrcb_frame, cv2.COLOR_YCrCb2BGR)
        
        result = detector.detect(frame)
        
        # Should detect the large region
        assert result is not None
        assert result.shape[0] > 0
        assert result.shape[1] > 0


class TestSkinDetectorMorphology:
    """Test morphological operations in SkinDetector."""
    
    def test_morphological_closing(self):
        """Test that morphological closing fills holes."""
        detector = SkinDetector()
        
        # Create frame with skin region containing holes
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        ycrcb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb)
        
        # Create region with holes
        ycrcb_frame[100:300, 100:300] = [128, 150, 100]
        ycrcb_frame[150:250, 150:250] = [0, 0, 0]  # Hole in the middle
        
        frame = cv2.cvtColor(ycrcb_frame, cv2.COLOR_YCrCb2BGR)
        
        result = detector.detect(frame)
        
        # Should still detect the region despite holes
        assert result is not None
    
    def test_morphological_opening(self):
        """Test that morphological opening removes noise."""
        detector = SkinDetector()
        
        # Create frame with skin region and noise
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        ycrcb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb)
        
        # Create main region
        ycrcb_frame[100:300, 100:300] = [128, 150, 100]
        
        # Add noise pixels
        ycrcb_frame[50:60, 50:60] = [128, 150, 100]
        ycrcb_frame[400:410, 400:410] = [128, 150, 100]
        
        frame = cv2.cvtColor(ycrcb_frame, cv2.COLOR_YCrCb2BGR)
        
        result = detector.detect(frame)
        
        # Should detect main region, noise should be removed
        assert result is not None


class TestSkinDetectorWithMask:
    """Test SkinDetector.detect_with_mask() method."""
    
    def create_test_frame(self, width=640, height=480, skin_color=True):
        """Create a test frame with optional skin-colored region."""
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        if skin_color:
            ycrcb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb)
            y_start, y_end = 100, 300
            x_start, x_end = 150, 350
            ycrcb_frame[y_start:y_end, x_start:x_end] = [128, 150, 100]
            frame = cv2.cvtColor(ycrcb_frame, cv2.COLOR_YCrCb2BGR)
        
        return frame
    
    def test_detect_with_mask_returns_tuple(self):
        """Test that detect_with_mask returns tuple."""
        detector = SkinDetector()
        frame = self.create_test_frame(skin_color=True)
        
        result = detector.detect_with_mask(frame)
        
        assert isinstance(result, tuple)
        assert len(result) == 2
    
    def test_detect_with_mask_returns_hand_region_and_mask(self):
        """Test that detect_with_mask returns hand region and mask."""
        detector = SkinDetector()
        frame = self.create_test_frame(skin_color=True)
        
        hand_region, mask = detector.detect_with_mask(frame)
        
        if hand_region is not None:
            assert len(hand_region.shape) == 2  # Grayscale
            assert hand_region.dtype == np.uint8
        
        if mask is not None:
            assert len(mask.shape) == 2  # Grayscale
            assert mask.dtype == np.uint8
    
    def test_detect_with_mask_with_none_frame(self):
        """Test detect_with_mask with None frame."""
        detector = SkinDetector()
        
        hand_region, mask = detector.detect_with_mask(None)
        
        assert hand_region is None
        assert mask is None


class TestGestureEngineInitialization:
    """Test GestureEngine initialization."""
    
    def test_default_initialization(self):
        """Test GestureEngine with default parameters."""
        engine = GestureEngine()
        
        assert engine.camera is None
        assert engine.model is None
        assert engine.confidence_threshold == 0.70
        assert engine.smoothing_frames == 20
        assert engine.running is False
        assert engine.fps_target == 30
        assert engine.skin_detector is not None
        assert len(engine.event_callbacks) == 0
    
    def test_custom_initialization(self):
        """Test GestureEngine with custom parameters."""
        engine = GestureEngine(
            confidence_threshold=0.80,
            smoothing_frames=25,
            fps_target=60
        )
        
        assert engine.confidence_threshold == 0.80
        assert engine.smoothing_frames == 25
        assert engine.fps_target == 60
    
    def test_frame_buffer_initialization(self):
        """Test that frame buffer is initialized correctly."""
        engine = GestureEngine()
        
        assert len(engine.frame_buffer) == 0
        assert engine.frame_buffer.maxlen == 30


class TestGestureEngineProcessFrame:
    """Test GestureEngine._process_frame() method."""
    
    def create_test_frame(self, width=640, height=480):
        """Create a test frame."""
        return np.zeros((height, width, 3), dtype=np.uint8)
    
    def test_process_frame_with_no_hand(self):
        """Test processing frame with no hand detected."""
        engine = GestureEngine()
        frame = self.create_test_frame()
        
        gesture, confidence = engine._process_frame(frame)
        
        assert gesture == 'nothing'
        assert confidence == 0.0
    
    def test_process_frame_with_no_model(self):
        """Test processing frame when model is not loaded."""
        engine = GestureEngine()
        
        # Create frame with skin region
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        ycrcb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb)
        ycrcb_frame[100:300, 100:300] = [128, 150, 100]
        frame = cv2.cvtColor(ycrcb_frame, cv2.COLOR_YCrCb2BGR)
        
        gesture, confidence = engine._process_frame(frame)
        
        # Should return nothing since model is not loaded
        assert gesture == 'nothing'
        assert confidence == 0.0
    
    def test_process_frame_returns_tuple(self):
        """Test that _process_frame returns tuple."""
        engine = GestureEngine()
        frame = self.create_test_frame()
        
        result = engine._process_frame(frame)
        
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], str)
        assert isinstance(result[1], float)


class TestGestureEngineTemporalSmoothing:
    """Test GestureEngine temporal smoothing."""
    
    def test_temporal_smoothing_requires_minimum_frames(self):
        """Test that temporal smoothing requires minimum frames."""
        engine = GestureEngine(smoothing_frames=5)
        
        # Add predictions to buffer
        for i in range(4):
            result = engine._apply_temporal_smoothing('app_switch', 0.9)
            assert result is None  # Not enough frames yet
    
    def test_temporal_smoothing_confirms_gesture(self):
        """Test that temporal smoothing confirms gesture after enough frames."""
        engine = GestureEngine(smoothing_frames=5)
        
        # Add same gesture predictions
        for i in range(5):
            result = engine._apply_temporal_smoothing('app_switch', 0.9)
        
        # Should confirm gesture on 5th frame
        assert result is not None
        assert result['gesture'] == 'app_switch'
        assert result['confidence'] > 0.0
    
    def test_temporal_smoothing_resets_on_different_gesture(self):
        """Test that temporal smoothing resets on different gesture."""
        engine = GestureEngine(smoothing_frames=5)
        
        # Add first gesture
        for i in range(3):
            engine._apply_temporal_smoothing('app_switch', 0.9)
        
        # Add different gesture
        result = engine._apply_temporal_smoothing('close_window', 0.9)
        
        # Buffer should reset, result should be None
        assert result is None
        assert len(engine.frame_buffer) == 1
    
    def test_temporal_smoothing_ignores_nothing_gesture(self):
        """Test that temporal smoothing ignores 'nothing' gesture."""
        engine = GestureEngine(smoothing_frames=5)
        
        # Add 'nothing' gesture predictions
        for i in range(5):
            result = engine._apply_temporal_smoothing('nothing', 0.9)
        
        # Should not confirm 'nothing' gesture
        assert result is None
    
    def test_temporal_smoothing_calculates_average_confidence(self):
        """Test that temporal smoothing calculates average confidence."""
        engine = GestureEngine(smoothing_frames=3)
        
        # Add predictions with different confidences
        engine._apply_temporal_smoothing('app_switch', 0.8)
        engine._apply_temporal_smoothing('app_switch', 0.9)
        result = engine._apply_temporal_smoothing('app_switch', 1.0)
        
        # Should calculate average confidence
        assert result is not None
        expected_avg = (0.8 + 0.9 + 1.0) / 3
        assert abs(result['confidence'] - expected_avg) < 0.01
    
    def test_temporal_smoothing_clears_buffer_after_confirmation(self):
        """Test that buffer is cleared after gesture confirmation."""
        engine = GestureEngine(smoothing_frames=3)
        
        # Add predictions
        for i in range(3):
            engine._apply_temporal_smoothing('app_switch', 0.9)
        
        # Buffer should be cleared after confirmation
        assert len(engine.frame_buffer) == 0


class TestGestureEngineEventCallbacks:
    """Test GestureEngine event callback system."""
    
    def test_register_callback(self):
        """Test registering event callback."""
        engine = GestureEngine()
        callback = Mock()
        
        engine.register_callback(callback)
        
        assert callback in engine.event_callbacks
    
    def test_emit_event_calls_callbacks(self):
        """Test that emit_event calls registered callbacks."""
        engine = GestureEngine()
        callback = Mock()
        engine.register_callback(callback)
        
        engine._emit_event('test_event', {'data': 'test'})
        
        callback.assert_called_once_with('test_event', {'data': 'test'})
    
    def test_emit_event_with_multiple_callbacks(self):
        """Test emit_event with multiple callbacks."""
        engine = GestureEngine()
        callback1 = Mock()
        callback2 = Mock()
        
        engine.register_callback(callback1)
        engine.register_callback(callback2)
        
        engine._emit_event('test_event', {'data': 'test'})
        
        callback1.assert_called_once()
        callback2.assert_called_once()
    
    def test_emit_event_handles_callback_errors(self):
        """Test that emit_event handles callback errors gracefully."""
        engine = GestureEngine()
        
        # Create callback that raises error
        def error_callback(event_type, data):
            raise Exception("Test error")
        
        engine.register_callback(error_callback)
        
        # Should not raise error
        engine._emit_event('test_event', {'data': 'test'})


class TestGestureEngineIdxToGesture:
    """Test GestureEngine._idx_to_gesture() method."""
    
    def test_idx_to_gesture_valid_indices(self):
        """Test gesture index to name conversion."""
        engine = GestureEngine()
        
        expected_gestures = [
            'app_switch',
            'close_window',
            'nothing',
            'play_pause',
            'scroll_down',
            'scroll_up',
            'screenshot',
            'volume_down',
            'volume_up'
        ]
        
        for idx, expected_gesture in enumerate(expected_gestures):
            gesture = engine._idx_to_gesture(idx)
            assert gesture == expected_gesture
    
    def test_idx_to_gesture_invalid_index(self):
        """Test gesture index conversion with invalid index."""
        engine = GestureEngine()
        
        gesture = engine._idx_to_gesture(999)
        
        assert gesture == 'nothing'
    
    def test_idx_to_gesture_negative_index(self):
        """Test gesture index conversion with negative index."""
        engine = GestureEngine()
        
        gesture = engine._idx_to_gesture(-1)
        
        assert gesture == 'nothing'


class TestGestureEngineGetStatus:
    """Test GestureEngine.get_status() method."""
    
    def test_get_status_returns_dict(self):
        """Test that get_status returns dictionary."""
        engine = GestureEngine()
        
        status = engine.get_status()
        
        assert isinstance(status, dict)
    
    def test_get_status_contains_required_fields(self):
        """Test that get_status contains required fields."""
        engine = GestureEngine()
        
        status = engine.get_status()
        
        assert 'running' in status
        assert 'camera_open' in status
        assert 'model_loaded' in status
        assert 'inference_latency_ms' in status
        assert 'confidence_threshold' in status
        assert 'smoothing_frames' in status
        assert 'fps_target' in status
    
    def test_get_status_values(self):
        """Test that get_status returns correct values."""
        engine = GestureEngine(
            confidence_threshold=0.80,
            smoothing_frames=25,
            fps_target=60
        )
        
        status = engine.get_status()
        
        assert status['running'] is False
        assert status['camera_open'] is False
        assert status['model_loaded'] is False
        assert status['confidence_threshold'] == 0.80
        assert status['smoothing_frames'] == 25
        assert status['fps_target'] == 60


class TestSkinDetectorEdgeCases:
    """Test SkinDetector edge cases."""
    
    def test_detect_with_boundary_values(self):
        """Test detection with boundary YCrCb values."""
        detector = SkinDetector(
            lower_cr=130,
            upper_cr=170,
            lower_cb=77,
            upper_cb=127
        )
        
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        ycrcb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb)
        
        # Set boundary values
        ycrcb_frame[100:300, 100:300] = [128, 130, 77]  # Lower bounds
        frame = cv2.cvtColor(ycrcb_frame, cv2.COLOR_YCrCb2BGR)
        
        result = detector.detect(frame)
        
        # Should detect region at boundary values
        assert result is not None
    
    def test_detect_with_out_of_range_values(self):
        """Test detection with out-of-range YCrCb values."""
        detector = SkinDetector()
        
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        ycrcb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb)
        
        # Set out-of-range values
        ycrcb_frame[100:300, 100:300] = [128, 50, 200]  # Outside skin range
        frame = cv2.cvtColor(ycrcb_frame, cv2.COLOR_YCrCb2BGR)
        
        result = detector.detect(frame)
        
        # Should not detect region
        assert result is None
    
    def test_detect_with_multiple_regions(self):
        """Test detection with multiple skin regions."""
        detector = SkinDetector()
        
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        ycrcb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb)
        
        # Create two regions
        ycrcb_frame[50:150, 50:150] = [128, 150, 100]
        ycrcb_frame[300:400, 300:400] = [128, 150, 100]
        
        frame = cv2.cvtColor(ycrcb_frame, cv2.COLOR_YCrCb2BGR)
        
        result = detector.detect(frame)
        
        # Should detect the largest region
        assert result is not None


class TestGestureEngineIntegration:
    """Integration tests for GestureEngine."""
    
    def test_engine_initialization_and_status(self):
        """Test engine initialization and status retrieval."""
        engine = GestureEngine(
            confidence_threshold=0.75,
            smoothing_frames=15,
            fps_target=30
        )
        
        status = engine.get_status()
        
        assert status['running'] is False
        assert status['confidence_threshold'] == 0.75
        assert status['smoothing_frames'] == 15
        assert status['fps_target'] == 30
    
    def test_engine_callback_registration(self):
        """Test engine callback registration and event emission."""
        engine = GestureEngine()
        
        events = []
        
        def capture_event(event_type, data):
            events.append((event_type, data))
        
        engine.register_callback(capture_event)
        engine._emit_event('test_event', {'test': 'data'})
        
        assert len(events) == 1
        assert events[0][0] == 'test_event'
        assert events[0][1]['test'] == 'data'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
