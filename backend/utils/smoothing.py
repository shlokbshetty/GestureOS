"""
Temporal Smoothing Algorithm

Smoothes predictions across consecutive frames to prevent jitter and
eliminate false positives from brief hand movements or noise.

Requirements: 1.6, 7.0
"""

import threading
from collections import deque
from typing import Dict, List, Optional, Tuple
import numpy as np


class TemporalSmoother:
    """
    Smooth predictions across multiple video frames.
    
    Algorithm:
    1. Maintain a FIFO buffer of recent (gesture, confidence) predictions.
    2. Check if the buffer contains at least `smoothing_frames` predictions.
    3. If all recent frames match the same gesture (and not 'nothing') with
       average confidence meeting threshold, confirm the gesture.
    4. Reset buffer upon confirmation or gesture change to prevent continuous false triggers.
    """
    
    def __init__(self, smoothing_frames: int = 20, min_confidence: float = 0.70):
        """
        Initialize TemporalSmoother.
        
        Args:
            smoothing_frames: Number of consecutive matching frames required (5-100).
            min_confidence: Minimum average confidence threshold (0.0 - 1.0).
        """
        if smoothing_frames < 1:
            raise ValueError("smoothing_frames must be >= 1")
        
        self.smoothing_frames = smoothing_frames
        self.min_confidence = min_confidence
        self.frame_buffer: deque = deque(maxlen=smoothing_frames)
        self.lock = threading.RLock()
    
    def add_prediction(self, gesture: str, confidence: float) -> Optional[Dict]:
        """
        Add a frame prediction and check if the gesture is confirmed.
        
        Args:
            gesture: Predicted gesture name.
            confidence: Prediction confidence score (0.0 to 1.0).
            
        Returns:
            Dict containing 'gesture', 'confidence', and 'frames' if confirmed,
            otherwise None.
        """
        with self.lock:
            self.frame_buffer.append((gesture, float(confidence)))
            
            # Need minimum frames before confirmation
            if len(self.frame_buffer) < self.smoothing_frames:
                return None
            
            # Inspect all frames in buffer
            gestures = [g for g, _ in self.frame_buffer]
            
            # Check if all frames have the same gesture and it is not 'nothing'
            if len(set(gestures)) == 1 and gestures[0] != 'nothing':
                avg_confidence = float(np.mean([c for _, c in self.frame_buffer]))
                
                if avg_confidence >= self.min_confidence:
                    confirmed_gesture = gestures[0]
                    # Reset buffer after confirmation to prevent duplicate triggers
                    self.frame_buffer.clear()
                    
                    return {
                        'gesture': confirmed_gesture,
                        'confidence': avg_confidence,
                        'frames': self.smoothing_frames
                    }
            
            return None
    
    def reset(self) -> None:
        """Clear the frame buffer."""
        with self.lock:
            self.frame_buffer.clear()
    
    def get_buffer(self) -> List[Tuple[str, float]]:
        """
        Get current frame buffer contents.
        
        Returns:
            List of (gesture, confidence) tuples.
        """
        with self.lock:
            return list(self.frame_buffer)
    
    def update_parameters(
        self,
        smoothing_frames: Optional[int] = None,
        min_confidence: Optional[float] = None
    ) -> None:
        """
        Update smoother parameters at runtime.
        
        Args:
            smoothing_frames: New smoothing frames count (optional).
            min_confidence: New confidence threshold (optional).
        """
        with self.lock:
            if smoothing_frames is not None:
                if smoothing_frames < 1:
                    raise ValueError("smoothing_frames must be >= 1")
                self.smoothing_frames = smoothing_frames
                self.frame_buffer = deque(maxlen=smoothing_frames)
            
            if min_confidence is not None:
                self.min_confidence = min_confidence
