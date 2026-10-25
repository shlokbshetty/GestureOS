"""
Gesture Recognition Engine - Vision Pipeline

This module implements the core vision pipeline for real-time gesture recognition:
- Camera capture and frame processing at 30 FPS
- YCrCb skin detection algorithm for hand region isolation
- High-performance ONNX / CNN inference for gesture classification
- Temporal smoothing for stable predictions
- Event emission for detected gestures and errors

Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 13.0, 17.0
"""

import threading
import time
from collections import deque
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple
import logging

import cv2
import numpy as np

from backend.utils.logger import get_logger
from backend.models.model_runner import OptimizedGestureModel


class SkinDetector:
    """
    Detect hand region using YCrCb color space.
    
    YCrCb is robust to ambient lighting variations:
    - Cr: 130-170
    - Cb: 77-127
    
    Requirements: 1.2, 1.3
    """
    
    def __init__(
        self,
        lower_cr: int = 130,
        upper_cr: int = 170,
        lower_cb: int = 77,
        upper_cb: int = 127,
        morph_kernel_size: int = 5,
        padding: int = 10,
        logger: Optional[logging.Logger] = None,
    ):
        self.lower_cr = lower_cr
        self.upper_cr = upper_cr
        self.lower_cb = lower_cb
        self.upper_cb = upper_cb
        self.morph_kernel_size = morph_kernel_size
        self.padding = padding
        self.logger = logger or get_logger('skin_detector')
        
        # YCrCb color range
        self.lower_skin = np.array([0, self.lower_cr, self.lower_cb], dtype=np.uint8)
        self.upper_skin = np.array([255, self.upper_cr, self.upper_cb], dtype=np.uint8)
        
        # Morphological ellipse kernel
        self.kernel = cv2.getStructuringElement(
            cv2.MORPH_ELLIPSE, (self.morph_kernel_size, self.morph_kernel_size)
        )

    def detect_with_mask(self, frame: Optional[np.ndarray]) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
        """
        Detect hand region in frame and return both isolated hand region and binary mask.
        
        Args:
            frame: OpenCV BGR frame or None
            
        Returns:
            Tuple of (hand_region_gray, mask) or (None, None)
        """
        if frame is None or not isinstance(frame, np.ndarray) or frame.size == 0:
            return None, None
            
        try:
            ycrcb = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb)
            mask = cv2.inRange(ycrcb, self.lower_skin, self.upper_skin)
            
            # Morphological operations (close to fill holes, open to remove noise)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, self.kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, self.kernel)
            
            contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            if not contours:
                return None, mask
            
            # Largest contour by area (hand)
            largest_contour = max(contours, key=cv2.contourArea)
            if cv2.contourArea(largest_contour) < 100:  # Minimum hand contour area
                return None, mask

            x, y, w, h = cv2.boundingRect(largest_contour)
            
            # Extract with padding
            x_pad = max(0, x - self.padding)
            y_pad = max(0, y - self.padding)
            w_pad = min(frame.shape[1] - x_pad, w + 2 * self.padding)
            h_pad = min(frame.shape[0] - y_pad, h + 2 * self.padding)
            
            hand_region = frame[y_pad:y_pad+h_pad, x_pad:x_pad+w_pad]
            if hand_region.size == 0:
                return None, mask
                
            hand_region_gray = cv2.cvtColor(hand_region, cv2.COLOR_BGR2GRAY)
            return hand_region_gray, mask
            
        except Exception as e:
            self.logger.error(f"Skin detection failed: {e}")
            return None, None

    def detect(self, frame: Optional[np.ndarray]) -> Optional[np.ndarray]:
        """
        Detect hand region in frame.
        
        Returns:
            Isolated hand region (grayscale) or None if not found
        """
        hand_region_gray, _ = self.detect_with_mask(frame)
        return hand_region_gray


class GestureEngine:
    """
    Vision pipeline orchestrating frame capture, inference, and temporal smoothing.
    
    Requirements: 1.1, 1.4, 1.7, 1.8, 1.9, 13.0, 17.0
    """
    
    GESTURE_CLASSES = [
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
    
    def __init__(
        self,
        model_path: Optional[str] = None,
        confidence_threshold: float = 0.70,
        smoothing_frames: int = 20,
        fps_target: int = 30,
        logger: Optional[logging.Logger] = None,
    ):
        self.logger = logger or get_logger('gesture_engine')
        self.confidence_threshold = confidence_threshold
        self.smoothing_frames = smoothing_frames
        self.fps_target = fps_target
        
        # Initialize model
        self.model = None
        if model_path is not None:
            self.model = self._load_model(model_path)
        
        # Camera and processing thread
        self.camera = None
        self.running = False
        self.processing_thread = None
        
        # Performance tracking
        self.inference_latency = 0.0
        self.frame_count = 0
        self.last_frame_time = time.time()
        
        # Prediction smoothing buffer
        self.frame_buffer = deque(maxlen=30)
        self.current_gesture = 'nothing'
        self.current_confidence = 0.0
        
        # Skin detector
        self.skin_detector = SkinDetector(logger=self.logger)
        
        # Callbacks & Thread safety
        self.event_callbacks: List[Callable] = []
        self.lock = threading.RLock()
    
    def _load_model(self, model_path: str) -> OptimizedGestureModel:
        """Load optimized ONNX or Keras model via OptimizedGestureModel."""
        p = Path(model_path)
        if not p.exists():
            # Check default ONNX path
            default_onnx = Path("backend/models/gesture_model.onnx")
            if default_onnx.exists():
                p = default_onnx
            else:
                self.logger.warning(f"Specified model path not found: {model_path}")
        return OptimizedGestureModel(str(p), logger=self.logger)
    
    def start(self) -> bool:
        """Initialize camera and start processing thread."""
        with self.lock:
            if self.running:
                return True
                
            try:
                self.camera = cv2.VideoCapture(0)
                if not self.camera.isOpened():
                    self.camera = cv2.VideoCapture(1)
                
                if not self.camera.isOpened():
                    error_msg = "No camera available (tried devices 0 and 1)"
                    self.logger.error(error_msg)
                    self._emit_event('camera_error', {'message': error_msg})
                    return False
                
                self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                self.camera.set(cv2.CAP_PROP_FPS, self.fps_target)
                
                self.running = True
                self.processing_thread = threading.Thread(
                    target=self._process_loop,
                    daemon=True,
                    name="GestureEngine-Thread",
                )
                self.processing_thread.start()
                self.logger.info("Camera initialized and processing thread started")
                return True
                
            except Exception as e:
                self.logger.error(f"Failed to start engine: {e}")
                self._emit_event('camera_error', {'message': str(e)})
                return False
    
    def stop(self) -> None:
        """Stop processing and release camera."""
        with self.lock:
            if not self.running:
                return
            self.running = False
            
        if self.processing_thread and self.processing_thread.is_alive():
            self.processing_thread.join(timeout=3)
            
        if self.camera:
            try:
                self.camera.release()
            except Exception:
                pass
            self.camera = None
            
        self.logger.info("GestureEngine stopped")
    
    def _process_loop(self) -> None:
        """Processing loop running at target FPS."""
        frame_interval = 1.0 / self.fps_target
        
        while self.running:
            loop_start = time.time()
            if self.camera and self.camera.isOpened():
                ret, frame = self.camera.read()
                if ret and frame is not None:
                    self.frame_count += 1
                    gesture, confidence = self._process_frame(frame)
                    
                    confirmed = self._apply_temporal_smoothing(gesture, confidence)
                    if confirmed:
                        self.current_gesture = confirmed['gesture']
                        self.current_confidence = confirmed['confidence']
                        self._emit_event('gesture_detected', {
                            'gesture': confirmed['gesture'],
                            'confidence': confirmed['confidence'],
                            'timestamp': time.time(),
                        })
            
            elapsed = time.time() - loop_start
            sleep_time = max(0.001, frame_interval - elapsed)
            time.sleep(sleep_time)

    def _process_frame(self, frame: np.ndarray) -> Tuple[str, float]:
        """Process a frame through detection, inference, and thresholding."""
        start_time = time.time()
        
        if self.model is None:
            return 'nothing', 0.0
            
        try:
            hand_region = self.skin_detector.detect(frame)
            if hand_region is None:
                return 'nothing', 0.0
                
            gesture_name, confidence = self.model.predict(hand_region)
            self.inference_latency = (time.time() - start_time) * 1000.0
            
            if confidence < self.confidence_threshold:
                return 'nothing', 0.0
                
            return gesture_name, confidence
            
        except Exception as e:
            self.logger.error(f"Frame processing error: {e}")
            return 'nothing', 0.0

    def _apply_temporal_smoothing(self, gesture: str, confidence: float) -> Optional[Dict]:
        """Apply temporal smoothing over frame buffer."""
        with self.lock:
            # Check if different from previous gesture in buffer
            if self.frame_buffer and self.frame_buffer[-1][0] != gesture:
                self.frame_buffer.clear()

            self.frame_buffer.append((gesture, float(confidence)))
            
            if len(self.frame_buffer) < self.smoothing_frames:
                return None
                
            recent_frames = list(self.frame_buffer)[-self.smoothing_frames:]
            gestures = [g for g, _ in recent_frames]
            
            if len(set(gestures)) == 1 and gestures[0] != 'nothing':
                avg_confidence = float(np.mean([c for _, c in recent_frames]))
                confirmed_gesture = gestures[0]
                self.frame_buffer.clear()
                return {
                    'gesture': confirmed_gesture,
                    'confidence': avg_confidence,
                }
                
            return None

    def _idx_to_gesture(self, idx: int) -> str:
        """Convert class index to gesture name."""
        if 0 <= idx < len(self.GESTURE_CLASSES):
            return self.GESTURE_CLASSES[idx]
        return 'nothing'

    def _emit_event(self, event_type: str, data: Dict) -> None:
        """Emit event to registered callbacks."""
        with self.lock:
            for callback in self.event_callbacks:
                try:
                    callback(event_type, data)
                except Exception as e:
                    self.logger.error(f"Error in event callback: {e}")

    def register_callback(self, callback: Callable) -> None:
        """Register an event callback."""
        with self.lock:
            if callback not in self.event_callbacks:
                self.event_callbacks.append(callback)

    def get_status(self) -> Dict:
        """Return engine status dictionary."""
        with self.lock:
            camera_open = bool(self.camera and self.camera.isOpened()) if self.camera else False
            model_loaded = (
                self.model is not None and getattr(self.model, 'backend_type', 'none') != 'none'
            )
            return {
                'running': self.running,
                'camera_open': camera_open,
                'model_loaded': model_loaded,
                'inference_latency_ms': self.inference_latency,
                'confidence_threshold': self.confidence_threshold,
                'smoothing_frames': self.smoothing_frames,
                'fps_target': self.fps_target,
            }

    def get_inference_latency(self) -> float:
        return self.inference_latency

    def get_frame_count(self) -> int:
        return self.frame_count

    def get_current_gesture(self) -> Tuple[str, float]:
        with self.lock:
            return self.current_gesture, self.current_confidence
