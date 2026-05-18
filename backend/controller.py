"""
Windows System Controller Module

This module provides cross-platform keyboard and mouse automation capabilities
for executing system actions triggered by gesture recognition.

Uses pynput for cross-platform compatibility and pyautogui for mouse operations.
"""

import time
import threading
from typing import Callable, Dict, List, Optional
from pynput.keyboard import Controller as KeyboardController, Key
from pynput.mouse import Controller as MouseController
import logging

logger = logging.getLogger(__name__)


class WindowsController:
    """
    Execute system actions on Windows via keyboard/mouse/media keys.
    
    This controller provides methods to execute various system actions including:
    - Keyboard shortcuts (Alt+Tab, Alt+F4)
    - Single key presses (Space, Print Screen)
    - Media keys (Volume Up/Down, Play/Pause)
    - Mouse scrolling
    
    Uses pynput for cross-platform compatibility.
    
    Attributes:
        keyboard: pynput KeyboardController instance
        mouse: pynput MouseController instance
        action_callbacks: List of callbacks for action events
        lock: Threading lock for thread-safe operations
    """
    
    def __init__(self, logger_instance=None):
        """
        Initialize the Windows Controller.
        
        Args:
            logger_instance: Optional logger instance for logging actions
        """
        self.keyboard = KeyboardController()
        self.mouse = MouseController()
        self.action_callbacks: List[Callable] = []
        self.lock = threading.RLock()
        self.logger = logger_instance or logger
        
    def execute_action(self, action_type: str, params: Optional[Dict] = None) -> bool:
        """
        Execute system action based on action type.
        
        Supported action types:
        - app_switch: Alt+Tab keyboard shortcut
        - close_window: Alt+F4 keyboard shortcut
        - play_pause: Space key press
        - volume_up: Volume Up media key
        - volume_down: Volume Down media key
        - scroll_up: Mouse scroll up (200 units)
        - scroll_down: Mouse scroll down (200 units)
        - screenshot: Print Screen key
        
        Args:
            action_type: Type of action to execute
            params: Optional parameters for the action
        
        Returns:
            True if successful, False otherwise
        """
        try:
            with self.lock:
                if action_type == 'app_switch':
                    self._keyboard_shortcut(['alt', 'tab'])
                elif action_type == 'close_window':
                    self._keyboard_shortcut(['alt', 'f4'])
                elif action_type == 'play_pause':
                    self._keyboard_key('space')
                elif action_type == 'volume_up':
                    self._media_key('volume_up')
                elif action_type == 'volume_down':
                    self._media_key('volume_down')
                elif action_type == 'scroll_up':
                    self._mouse_scroll(200)
                elif action_type == 'scroll_down':
                    self._mouse_scroll(-200)
                elif action_type == 'screenshot':
                    self._keyboard_key('print_screen')
                else:
                    self.logger.warning(f'Unknown action type: {action_type}')
                    self._emit_callback('action_failed', {
                        'action': action_type,
                        'error': f'Unknown action type: {action_type}'
                    })
                    return False
                
                self.logger.info(f'Action executed: {action_type}')
                self._emit_callback('action_executed', {'action': action_type})
                return True
        
        except Exception as e:
            self.logger.error(f'Action execution failed: {action_type}, {str(e)}')
            self._emit_callback('action_failed', {
                'action': action_type,
                'error': str(e)
            })
            return False
    
    def _keyboard_shortcut(self, keys: List[str]) -> None:
        """
        Execute keyboard shortcut with multiple keys pressed simultaneously.
        
        Example: _keyboard_shortcut(['alt', 'tab']) executes Alt+Tab
        
        Args:
            keys: List of key names to press (e.g., ['alt', 'tab'])
        
        Raises:
            Exception: If key is not recognized
        """
        # Convert key names to pynput Key objects
        key_objects = []
        for key_name in keys:
            key_obj = self._get_key_object(key_name)
            if key_obj is None:
                raise ValueError(f'Unknown key: {key_name}')
            key_objects.append(key_obj)
        
        # Press all keys
        for key_obj in key_objects:
            self.keyboard.press(key_obj)
            time.sleep(0.05)  # Small delay between key presses
        
        # Release all keys in reverse order
        for key_obj in reversed(key_objects):
            self.keyboard.release(key_obj)
            time.sleep(0.05)  # Small delay between key releases
    
    def _keyboard_key(self, key_name: str) -> None:
        """
        Press and release a single keyboard key.
        
        Args:
            key_name: Name of the key to press (e.g., 'space', 'print_screen')
        
        Raises:
            Exception: If key is not recognized
        """
        key_obj = self._get_key_object(key_name)
        if key_obj is None:
            raise ValueError(f'Unknown key: {key_name}')
        
        self.keyboard.press(key_obj)
        time.sleep(0.05)
        self.keyboard.release(key_obj)
    
    def _media_key(self, key_name: str) -> None:
        """
        Execute media key (volume, play, etc.).
        
        Supported media keys:
        - volume_up: Increase volume
        - volume_down: Decrease volume
        - play_pause: Play/pause media
        
        Args:
            key_name: Name of the media key
        
        Raises:
            Exception: If media key is not supported
        """
        try:
            if key_name == 'volume_up':
                self.keyboard.press(Key.media_volume_up)
                time.sleep(0.05)
                self.keyboard.release(Key.media_volume_up)
            elif key_name == 'volume_down':
                self.keyboard.press(Key.media_volume_down)
                time.sleep(0.05)
                self.keyboard.release(Key.media_volume_down)
            elif key_name == 'play_pause':
                self.keyboard.press(Key.media_play_pause)
                time.sleep(0.05)
                self.keyboard.release(Key.media_play_pause)
            else:
                raise ValueError(f'Unknown media key: {key_name}')
        except AttributeError as e:
            # Media key might not be available on this platform
            self.logger.warning(f'Media key not available: {key_name}, {str(e)}')
            raise
    
    def _mouse_scroll(self, units: int) -> None:
        """
        Scroll mouse wheel.
        
        Args:
            units: Number of units to scroll (positive = up, negative = down)
        """
        self.mouse.scroll(0, units)
        time.sleep(0.1)  # Small delay after scroll
    
    def _get_key_object(self, key_name: str) -> Optional:
        """
        Convert key name string to pynput Key object.
        
        Supported keys:
        - Special keys: alt, ctrl, shift, tab, enter, space, escape, backspace
        - Function keys: f1-f12
        - Navigation: up, down, left, right, home, end, page_up, page_down
        - Other: print_screen, delete, insert
        
        Args:
            key_name: Name of the key (lowercase)
        
        Returns:
            pynput Key object or None if not found
        """
        key_name = key_name.lower().strip()
        
        # Map of key names to pynput Key objects
        key_map = {
            'alt': Key.alt,
            'alt_l': Key.alt_l,
            'alt_r': Key.alt_r,
            'ctrl': Key.ctrl,
            'ctrl_l': Key.ctrl_l,
            'ctrl_r': Key.ctrl_r,
            'shift': Key.shift,
            'shift_l': Key.shift_l,
            'shift_r': Key.shift_r,
            'tab': Key.tab,
            'enter': Key.enter,
            'return': Key.enter,
            'space': Key.space,
            'escape': Key.esc,
            'esc': Key.esc,
            'backspace': Key.backspace,
            'delete': Key.delete,
            'insert': Key.insert,
            'home': Key.home,
            'end': Key.end,
            'page_up': Key.page_up,
            'page_down': Key.page_down,
            'up': Key.up,
            'down': Key.down,
            'left': Key.left,
            'right': Key.right,
            'print_screen': Key.print_screen,
            'print': Key.print_screen,
            'f1': Key.f1,
            'f2': Key.f2,
            'f3': Key.f3,
            'f4': Key.f4,
            'f5': Key.f5,
            'f6': Key.f6,
            'f7': Key.f7,
            'f8': Key.f8,
            'f9': Key.f9,
            'f10': Key.f10,
            'f11': Key.f11,
            'f12': Key.f12,
        }
        
        return key_map.get(key_name)
    
    def register_callback(self, callback: Callable) -> None:
        """
        Register callback for action events.
        
        Callbacks will be called with (event_type, data) arguments.
        
        Args:
            callback: Callable that accepts (event_type, data) arguments
        """
        with self.lock:
            self.action_callbacks.append(callback)
    
    def _emit_callback(self, event_type: str, data: Dict) -> None:
        """
        Emit event to registered callbacks.
        
        Args:
            event_type: Type of event (e.g., 'action_executed', 'action_failed')
            data: Event data dictionary
        """
        for callback in self.action_callbacks:
            try:
                callback(event_type, data)
            except Exception as e:
                self.logger.error(f'Error in callback: {str(e)}')
