"""
Gesture Recognition Engine - Vision Pipeline

This module implements the core vision pipeline for real-time gesture recognition:
- Camera capture and frame processing at 30 FPS
- YCrCb skin detection algorithm for hand region isolation
- CNN inference for gesture classification
- Temporal smoothing for stable predictions
- Event emission for detected gestures and errors

Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 13.0, 17.0
"""

import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
import threading
import time
from collections import deque
from typing import Optional, Tuple, Dict, Callable, List
from pathlib import Path
import logging

from backend.utils.logger import get_logger


class SkinDetector:
    """
    Detect hand region using YCrCb color space.
    
    YCrCb is more robust to lighting changes than RGB.
    Skin pixels typically have:
    - Cr: 130-170
    - Cb: 77-127
    
    Responsibilities:
    - Convert frame to YCrCb color space
    - Apply skin color thresholding
    - Morphological operations for mask cleanup
    - Extract hand region with bounding box
    
    Requirements: 1.2, 1.3
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize SkinDetector.
        
        Args:
            logger: Logger instance for debug/error logging
        """
        self.logger = logger or get_logger('skin_detector')
        
        # YCrCb skin color range (empirically determined)
        self.lower_skin = np.array([0, 130, 77])
        self.upper_skin = np.array([255, 170, 127])
        
        # Morphological kernel for mask cleanup
        self.kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        
        # Padding for hand region extraction
        self.padding = 10
    
    def detect(self, frame: np.ndarray) -> Optional[np.ndarray]:
        """
        Detect hand region in frame.
        
        Algorithm:
        1. Convert BGR to YCrCb color space
        2. Apply skin color thresholding
        3. Morphological operations (close, open) for cleanup
        4. Find largest contour (hand)
        5. Extract hand region with padding
        6. Convert to grayscale for model input
        
        Args:
            frame: OpenCV frame (BGR format, shape: (height, width, 3))
        
        Returns:
            Isolated hand region (grayscale, shape: (h, w)) or None if not found
        """
        try:
            # Step 1: Convert BGR to YCrCb
            ycrcb = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb)
            
            # Step 2: Create mask using skin color range
            mask = cv2.inRange(ycrcb, self.lower_skin, self.upper_skin)
            
            # Step 3: Morphological operations to clean mask
            # Close: fill small holes in foreground
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, self.kernel)
            # Open: remove small noise
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, self.kernel)
            
            # Step 4: Find contours and get largest (hand)
            contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            
            if not contours:
                return None
            
            # Get largest contour by area
            largest_contour = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(largest_contour)
            
            # Step 5: Extract hand region with padding
            x = max(0, x - self.padding)
            y = max(0, y - self.padding)
            w = min(frame.shape[1] - x, w + 2 * self.padding)
            h = min(frame.shape[0] - y, h + 2 * self.padding)
            
            hand_region = frame[y:y+h, x:x+w]
            
            if hand_region.size == 0:
                return None
            
            # Step 6: Convert to grayscale for model input
            hand_region_gray = cv2.cvtColor(hand_region, cv2.COLOR_BGR2GRAY)
            
            return hand_region_gray
        
        except Exception as e:
            self.logger.error(f"Skin detection failed: {e}")
            return None


class GestureEngine:
    """
    Core vision pipeline for real-time gesture recognition.
    
    Responsibilities:
    - Camera capture and frame processing at 30 FPS
    - Skin detection using YCrCb color space
    - CNN inference for gesture classification
    - Temporal smoothing for stable predictions
    - Event emission for detected gestures and errors
    - Performance monitoring (inference latency, frame rate)
    
    Attributes:
        camera: OpenCV VideoCapture object
        model: Loaded TensorFlow/Keras CNN model
        frame_buffer: Deque tracking recent gesture predictions
        confidence_threshold: Minimum confidence for acceptance (default 70%)
        smoothing_frames: Frames required for gesture confirmation (default 20)
        running: Boolean flag for engine state
        fps_target: Target frames per second (30)
        inference_latency: Time in ms for CNN inference
        event_callbacks: List of registered event callbacks
    
    Requirements: 1.1, 1.4, 1.7, 1.8, 1.9, 13.0, 17.0
    """
    
    # Gesture class names (must match model training order)
    GESTURE_CLASSES = [
        'app_switch',
        'close_window',
        'nothing',
        'play_pause',
        'screenshot',
        'scroll_down',
        'scroll_up',
        'volume_down',
        'volume_up'
    ]
    
    def __init__(
        self,
        model_path: str,
        confidence_threshold: float = 0.70,
        smoothing_frames: int = 20,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize GestureEngine.
        
        Args:
            model_path: Path to pre-trained CNN model (cnn_model_keras.h5)
            confidence_threshold: Minimum confidence for gesture acceptance (0.0-1.0)
            smoothing_frames: Number of frames required for gesture confirmation
            logger: Logger instance for debug/error logging
        
        Raises:
            FileNotFoundError: If model file not found
            Exception: If model loading fails
        """
        self.logger = logger or get_logger('gesture_engine')
        
        # Model and inference
        self.model = self._load_model(model_path)
        self.confidence_threshold = confidence_threshold
        self.smoothing_frames = smoothing_frames
        
        # Camera and processing
        self.camera = None
        self.running = False
        self.processing_thread = None
        
        # Performance tracking
        self.fps_target = 30
        self.inference_latency = 0.0  # milliseconds
        self.frame_count = 0
        self.last_frame_time = time.time()
        
        # Gesture tracking
        self.frame_buffer = deque(maxlen=30)  # Track last 30 predictions
        self.current_gesture = 'nothing'
        self.current_confidence = 0.0
        
        # Skin detection
        self.skin_detector = SkinDetector(logger=self.logger)
        
        # Event callbacks
        self.event_callbacks: List[Callable] = []
        
        # Thread safety
        self.lock = threading.RLock()
        
        self.logger.info(f"GestureEngine initialized with model: {model_path}")
        self.logger.info(f"Confidence threshold: {confidence_threshold:.2f}")
        self.logger.info(f"Smoothing frames: {smoothing_frames}")
    
    def _load_model(self, model_path: str) -> tf.keras.Model:
        """
        Load pre-trained CNN model from file.
        
        Args:
            model_path: Path to model file (cnn_model_keras.h5)
        
        Returns:
            Loaded TensorFlow/Keras model
        
        Raises:
            FileNotFoundError: If model file not found
            Exception: If model loading fails
        
        Requirements: 1.4
        """
        model_path = Path(model_path)
        
        if not model_path.exists():
            error_msg = f"Model file not found: {model_path}"
            self.logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        
        try:
            self.logger.info(f"Loading CNN model from: {model_path}")
            model = load_model(str(model_path))
            self.logger.info(f"Model loaded successfully")
            self.logger.debug(f"Model input shape: {model.input_shape}")
            self.logger.debug(f"Model output shape: {model.output_shape}")
            return model
        
        except Exception as e:
            error_msg = f"Failed to load model: {e}"
            self.logger.error(error_msg)
            raise
    
    def start(self) -> bool:
        """
        Initialize camera and start processing thread.
        
        Attempts to open camera device 0, falls back to device 1 if unavailable.
        Starts background processing thread for frame capture and inference.
        
        Returns:
            True if successful, False if camera unavailable
        
        Requirements: 1.1, 1.8, 13.0
        """
        with self.lock:
            if self.running:
                self.logger.warning("Engine already running")
                return True
            
            try:
                # Try to open camera device 0
                self.camera = cv2.VideoCapture(0)
                
                if not self.camera.isOpened():
                    self.logger.warning("Camera device 0 not available, trying device 1")
                    self.camera = cv2.VideoCapture(1)
                
                if not self.camera.isOpened():
                    error_msg = "No camera available (tried devices 0 and 1)"
                    self.logger.error(error_msg)
                    self._emit_event('camera_error', {'message': error_msg})
                    return False
                
                # Set camera properties
                self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                self.camera.set(cv2.CAP_PROP_FPS, self.fps_target)
                
                # Start processing thread
                self.running = True
                self.processing_thread = threading.Thread(
                    target=self._process_loop,
                    daemon=True,
                    name="GestureEngine-ProcessingThread"
                )
                self.processing_thread.start()
                
                self.logger.info("Camera initialized and processing thread started")
                return True
            
            except Exception as e:
                error_msg = f"Failed to initialize camera: {e}"
                self.logger.error(error_msg)
                self._emit_event('camera_error', {'message': error_msg})
                return False
    
    def stop(self) -> None:
        """
        Stop processing and release camera.
        
        Gracefully stops the processing thread and releases camera resources.
        Waits up to 5 seconds for thread termination.
        
        Requirements: 1.9, 10.0
        """
        with self.lock:
            if not self.running:
                return
            
            self.running = False
        
        # Wait for processing thread to finish (outside lock to avoid deadlock)
        if self.processing_thread and self.processing_thread.is_alive():
            self.logger.info("Waiting for processing thread to finish...")
            self.processing_thread.join(timeout=5)
            
            if self.processing_thread.is_alive():
                self.logger.warning("Processing thread did not terminate within timeout")
        
        # Release camera
        if self.camera:
            self.camera.release()
            self.logger.info("Camera released")
        
        self.logger.info("GestureEngine stopped")
    
    def _process_loop(self) -> None:
        """
        Main processing loop running at 30 FPS.
        
        Continuously:
        1. Capture frame from camera
        2. Process frame through vision pipeline
        3. Apply temporal smoothing
        4. Emit gesture_detected events
        5. Maintain target FPS
        
        Requirements: 1.1, 1.8, 17.0
        """
        frame_time_ms = 1000 / self.fps_target  # 33ms per frame at 30 FPS
        
        self.logger.info(f"Processing loop started (target FPS: {self.fps_target})")
        
        while self.running:
            try:
                start_time = time.time()
                
                # Capture frame
                ret, frame = self.camera.read()
                if not ret:
                    self.logger.error("Failed to read frame from camera")
                    self._emit_event('camera_error', {'message': 'Failed to read frame'})
                    time.sleep(0.1)
                    continue
                
                # Process frame through pipeline
                gesture, confidence = self._process_frame(frame)
                
                # Apply temporal smoothing
                confirmed_gesture = self._apply_temporal_smoothing(gesture, confidence)
                
                if confirmed_gesture:
                    self.logger.info(
                        f"Gesture confirmed: {confirmed_gesture['gesture']} "
                        f"(confidence: {confirmed_gesture['confidence']:.2f})"
                    )
                    self._emit_event('gesture_detected', {
                        'gesture': confirmed_gesture['gesture'],
                        'confidence': confirmed_gesture['confidence'],
                        'timestamp': time.time()
                    })
                
                # Update frame count and timing
                self.frame_count += 1
                
                # Maintain target FPS
                elapsed_ms = (time.time() - start_time) * 1000
                sleep_ms = max(0, frame_time_ms - elapsed_ms)
                
                if sleep_ms > 0:
                    time.sleep(sleep_ms / 1000)
            
            except Exception as e:
                self.logger.error(f"Error in processing loop: {e}")
                self._emit_event('camera_error', {'message': f'Processing error: {e}'})
                time.sleep(0.1)
        
        self.logger.info("Processing loop ended")
    
    def _process_frame(self, frame: np.ndarray) -> Tuple[str, float]:
        """
        Process single frame through vision pipeline.
        
        Pipeline:
        1. Skin detection to isolate hand region
        2. Image normalization (50x50, 0-1 range)
        3. CNN inference
        4. Confidence threshold check
        5. Track inference latency
        
        Args:
            frame: OpenCV frame (BGR format, shape: (height, width, 3))
        
        Returns:
            Tuple of (gesture_name, confidence_score)
        
        Requirements: 1.2, 1.3, 1.4, 1.5, 17.0
        """
        start_time = time.time()
        
        try:
            # Step 1: Skin detection
            hand_region = self.skin_detector.detect(frame)
            if hand_region is None:
                return 'nothing', 0.0
            
            # Step 2: Image normalization (50x50, 0-1 range)
            normalized = self._normalize_image(hand_region)
            
            # Step 3: CNN inference
            predictions = self.model.predict(normalized, verbose=0)
            gesture_idx = np.argmax(predictions[0])
            confidence = float(predictions[0][gesture_idx])
            
            # Step 4: Confidence threshold check
            if confidence < self.confidence_threshold:
                return 'nothing', 0.0
            
            gesture_name = self._idx_to_gesture(gesture_idx)
            
            # Step 5: Track inference latency
            self.inference_latency = (time.time() - start_time) * 1000
            
            return gesture_name, confidence
        
        except Exception as e:
            self.logger.error(f"Frame processing failed: {e}")
            return 'nothing', 0.0
    
    def _normalize_image(self, hand_region: np.ndarray) -> np.ndarray:
        """
        Normalize hand region image for CNN input.
        
        Normalization steps:
        1. Resize to 50x50 pixels
        2. Normalize pixel values to 0-1 range
        3. Reshape to (1, 50, 50, 1) for model input
        
        Args:
            hand_region: Grayscale hand region image
        
        Returns:
            Normalized image ready for CNN inference (shape: (1, 50, 50, 1))
        
        Requirements: 1.3, 1.4
        """
        # Resize to 50x50
        resized = cv2.resize(hand_region, (50, 50))
        
        # Normalize to 0-1 range
        normalized = resized.astype('float32') / 255.0
        
        # Reshape to (1, 50, 50, 1) for model input
        # Batch size: 1, Height: 50, Width: 50, Channels: 1
        reshaped = np.reshape(normalized, (1, 50, 50, 1))
        
        return reshaped
    
    def _apply_temporal_smoothing(self, gesture: str, confidence: float) -> Optional[Dict]:
        """
        Apply temporal smoothing to stabilize predictions.
        
        Algorithm:
        1. Add current prediction to frame buffer
        2. Count consecutive frames with same gesture
        3. If count >= smoothing_frames, confirm gesture
        4. If different gesture detected, reset buffer
        
        Args:
            gesture: Predicted gesture name
            confidence: Prediction confidence
        
        Returns:
            Dict with confirmed gesture or None if not confirmed
        
        Requirements: 1.6, 7.0
        """
        with self.lock:
            self.frame_buffer.append((gesture, confidence))
            
            # Need minimum frames before confirmation
            if len(self.frame_buffer) < self.smoothing_frames:
                return None
            
            # Check if last N frames have same gesture
            recent_frames = list(self.frame_buffer)[-self.smoothing_frames:]
            gestures = [g for g, _ in recent_frames]
            
            # All recent frames must have same gesture (and not 'nothing')
            if len(set(gestures)) == 1 and gestures[0] != 'nothing':
                # Calculate average confidence
                avg_confidence = np.mean([c for _, c in recent_frames])
                
                # Clear buffer after confirmation
                self.frame_buffer.clear()
                
                return {
                    'gesture': gestures[0],
                    'confidence': avg_confidence
                }
            
            return None
    
    def _idx_to_gesture(self, idx: int) -> str:
        """
        Convert gesture class index to gesture name.
        
        Args:
            idx: Gesture class index from model output
        
        Returns:
            Gesture name (e.g., 'app_switch')
        """
        if 0 <= idx < len(self.GESTURE_CLASSES):
            return self.GESTURE_CLASSES[idx]
        return 'nothing'
    
    def _emit_event(self, event_type: str, data: Dict) -> None:
        """
        Emit event to registered callbacks.
        
        Args:
            event_type: Type of event (e.g., 'gesture_detected', 'camera_error')
            data: Event data dictionary
        
        Requirements: 1.7, 1.9
        """
        with self.lock:
            for callback in self.event_callbacks:
                try:
                    callback(event_type, data)
                except Exception as e:
                    self.logger.error(f"Error in event callback: {e}")
    
    def register_callback(self, callback: Callable) -> None:
        """
        Register callback for engine events.
        
        Callbacks will be called with (event_type, data) arguments.
        
        Args:
            callback: Callable that accepts (event_type: str, data: dict)
        
        Requirements: 1.7
        """
        with self.lock:
            self.event_callbacks.append(callback)
            self.logger.debug(f"Event callback registered: {callback.__name__}")
    
    def get_inference_latency(self) -> float:
        """
        Get last measured inference latency in milliseconds.
        
        Returns:
            Inference latency in ms
        
        Requirements: 17.0
        """
        return self.inference_latency
    
    def get_frame_count(self) -> int:
        """
        Get total number of frames processed.
        
        Returns:
            Frame count
        """
        return self.frame_count
    
    def get_current_gesture(self) -> Tuple[str, float]:
        """
        Get current gesture and confidence.
        
        Returns:
            Tuple of (gesture_name, confidence)
        """
        with self.lock:
            return (self.current_gesture, self.current_confidence)
