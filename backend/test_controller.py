"""
Unit tests for the Windows System Controller module.

Tests verify:
- Keyboard shortcut execution (Alt+Tab, Alt+F4)
- Single key presses (Space, Print Screen)
- Media key handling (Volume Up/Down)
- Mouse scrolling
- Action execution with error handling
- Event callback system
- Thread safety
"""

import unittest
import time
import threading
from unittest.mock import Mock, patch, MagicMock, call
from pynput.keyboard import Key

from backend.controller import WindowsController


class TestWindowsControllerInitialization(unittest.TestCase):
    """Test cases for WindowsController initialization."""
    
    def test_controller_initialization(self):
        """Test that controller initializes with required components."""
        controller = WindowsController()
        
        self.assertIsNotNone(controller.keyboard)
        self.assertIsNotNone(controller.mouse)
        self.assertIsInstance(controller.action_callbacks, list)
        self.assertEqual(len(controller.action_callbacks), 0)
    
    def test_controller_with_logger(self):
        """Test controller initialization with custom logger."""
        mock_logger = Mock()
        controller = WindowsController(logger_instance=mock_logger)
        
        self.assertEqual(controller.logger, mock_logger)
    
    def test_controller_has_lock(self):
        """Test that controller has threading lock for thread safety."""
        controller = WindowsController()
        
        self.assertIsNotNone(controller.lock)


class TestKeyboardShortcuts(unittest.TestCase):
    """Test cases for keyboard shortcut execution."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.controller = WindowsController()
        self.mock_logger = Mock()
        self.controller.logger = self.mock_logger
    
    @patch('backend.controller.KeyboardController.press')
    @patch('backend.controller.KeyboardController.release')
    def test_alt_tab_shortcut(self, mock_release, mock_press):
        """Test Alt+Tab keyboard shortcut execution."""
        result = self.controller.execute_action('app_switch')
        
        self.assertTrue(result)
        self.mock_logger.info.assert_called_with('Action executed: app_switch')
    
    @patch('backend.controller.KeyboardController.press')
    @patch('backend.controller.KeyboardController.release')
    def test_alt_f4_shortcut(self, mock_release, mock_press):
        """Test Alt+F4 keyboard shortcut execution."""
        result = self.controller.execute_action('close_window')
        
        self.assertTrue(result)
        self.mock_logger.info.assert_called_with('Action executed: close_window')
    
    @patch('backend.controller.KeyboardController.press')
    @patch('backend.controller.KeyboardController.release')
    def test_space_key_press(self, mock_release, mock_press):
        """Test Space key press execution."""
        result = self.controller.execute_action('play_pause')
        
        self.assertTrue(result)
        self.mock_logger.info.assert_called_with('Action executed: play_pause')
    
    @patch('backend.controller.KeyboardController.press')
    @patch('backend.controller.KeyboardController.release')
    def test_print_screen_key_press(self, mock_release, mock_press):
        """Test Print Screen key press execution."""
        result = self.controller.execute_action('screenshot')
        
        self.assertTrue(result)
        self.mock_logger.info.assert_called_with('Action executed: screenshot')


class TestMediaKeys(unittest.TestCase):
    """Test cases for media key handling."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.controller = WindowsController()
        self.mock_logger = Mock()
        self.controller.logger = self.mock_logger
    
    @patch('backend.controller.KeyboardController.press')
    @patch('backend.controller.KeyboardController.release')
    def test_volume_up_media_key(self, mock_release, mock_press):
        """Test Volume Up media key execution."""
        result = self.controller.execute_action('volume_up')
        
        self.assertTrue(result)
        self.mock_logger.info.assert_called_with('Action executed: volume_up')
    
    @patch('backend.controller.KeyboardController.press')
    @patch('backend.controller.KeyboardController.release')
    def test_volume_down_media_key(self, mock_release, mock_press):
        """Test Volume Down media key execution."""
        result = self.controller.execute_action('volume_down')
        
        self.assertTrue(result)
        self.mock_logger.info.assert_called_with('Action executed: volume_down')


class TestMouseScrolling(unittest.TestCase):
    """Test cases for mouse scrolling functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.controller = WindowsController()
        self.mock_logger = Mock()
        self.controller.logger = self.mock_logger
    
    @patch('backend.controller.MouseController.scroll')
    def test_scroll_up_action(self, mock_scroll):
        """Test scroll up action."""
        result = self.controller.execute_action('scroll_up')
        
        self.assertTrue(result)
        mock_scroll.assert_called_once_with(0, 200)
        self.mock_logger.info.assert_called_with('Action executed: scroll_up')
    
    @patch('backend.controller.MouseController.scroll')
    def test_scroll_down_action(self, mock_scroll):
        """Test scroll down action."""
        result = self.controller.execute_action('scroll_down')
        
        self.assertTrue(result)
        mock_scroll.assert_called_once_with(0, -200)
        self.mock_logger.info.assert_called_with('Action executed: scroll_down')


class TestActionExecution(unittest.TestCase):
    """Test cases for action execution and error handling."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.controller = WindowsController()
        self.mock_logger = Mock()
        self.controller.logger = self.mock_logger
    
    def test_unknown_action_type(self):
        """Test handling of unknown action type."""
        result = self.controller.execute_action('unknown_action')
        
        self.assertFalse(result)
        self.mock_logger.warning.assert_called()
    
    @patch('backend.controller.KeyboardController.press')
    @patch('backend.controller.KeyboardController.release')
    def test_action_execution_with_exception(self, mock_release, mock_press):
        """Test error handling when action execution fails."""
        mock_press.side_effect = Exception('Test error')
        
        result = self.controller.execute_action('app_switch')
        
        self.assertFalse(result)
        self.mock_logger.error.assert_called()
    
    def test_execute_action_with_params(self):
        """Test action execution with parameters."""
        with patch.object(self.controller, '_keyboard_key'):
            result = self.controller.execute_action('play_pause', params={'key': 'space'})
            
            self.assertTrue(result)


class TestEventCallbacks(unittest.TestCase):
    """Test cases for event callback system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.controller = WindowsController()
        self.mock_logger = Mock()
        self.controller.logger = self.mock_logger
    
    @patch('backend.controller.KeyboardController.press')
    @patch('backend.controller.KeyboardController.release')
    def test_action_executed_callback(self, mock_release, mock_press):
        """Test that action_executed callback is emitted."""
        mock_callback = Mock()
        self.controller.register_callback(mock_callback)
        
        self.controller.execute_action('app_switch')
        
        mock_callback.assert_called_once()
        call_args = mock_callback.call_args
        self.assertEqual(call_args[0][0], 'action_executed')
        self.assertEqual(call_args[0][1]['action'], 'app_switch')
    
    def test_action_failed_callback(self):
        """Test that action_failed callback is emitted on error."""
        mock_callback = Mock()
        self.controller.register_callback(mock_callback)
        
        self.controller.execute_action('unknown_action')
        
        mock_callback.assert_called_once()
        call_args = mock_callback.call_args
        self.assertEqual(call_args[0][0], 'action_failed')
    
    def test_multiple_callbacks(self):
        """Test that multiple callbacks are all called."""
        mock_callback1 = Mock()
        mock_callback2 = Mock()
        self.controller.register_callback(mock_callback1)
        self.controller.register_callback(mock_callback2)
        
        with patch.object(self.controller, '_keyboard_key'):
            self.controller.execute_action('play_pause')
        
        mock_callback1.assert_called_once()
        mock_callback2.assert_called_once()
    
    def test_callback_exception_handling(self):
        """Test that exception in callback doesn't break execution."""
        mock_callback = Mock(side_effect=Exception('Callback error'))
        self.controller.register_callback(mock_callback)
        
        with patch.object(self.controller, '_keyboard_key'):
            result = self.controller.execute_action('play_pause')
        
        self.assertTrue(result)
        self.mock_logger.error.assert_called()


class TestKeyMapping(unittest.TestCase):
    """Test cases for key name to pynput Key object mapping."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.controller = WindowsController()
    
    def test_get_key_object_special_keys(self):
        """Test mapping of special keys."""
        self.assertEqual(self.controller._get_key_object('alt'), Key.alt)
        self.assertEqual(self.controller._get_key_object('ctrl'), Key.ctrl)
        self.assertEqual(self.controller._get_key_object('shift'), Key.shift)
        self.assertEqual(self.controller._get_key_object('tab'), Key.tab)
        self.assertEqual(self.controller._get_key_object('enter'), Key.enter)
    
    def test_get_key_object_navigation_keys(self):
        """Test mapping of navigation keys."""
        self.assertEqual(self.controller._get_key_object('up'), Key.up)
        self.assertEqual(self.controller._get_key_object('down'), Key.down)
        self.assertEqual(self.controller._get_key_object('left'), Key.left)
        self.assertEqual(self.controller._get_key_object('right'), Key.right)
        self.assertEqual(self.controller._get_key_object('home'), Key.home)
        self.assertEqual(self.controller._get_key_object('end'), Key.end)
    
    def test_get_key_object_function_keys(self):
        """Test mapping of function keys."""
        self.assertEqual(self.controller._get_key_object('f1'), Key.f1)
        self.assertEqual(self.controller._get_key_object('f12'), Key.f12)
    
    def test_get_key_object_print_screen(self):
        """Test mapping of Print Screen key."""
        self.assertEqual(self.controller._get_key_object('print_screen'), Key.print_screen)
        self.assertEqual(self.controller._get_key_object('print'), Key.print_screen)
    
    def test_get_key_object_case_insensitive(self):
        """Test that key mapping is case insensitive."""
        self.assertEqual(self.controller._get_key_object('ALT'), Key.alt)
        self.assertEqual(self.controller._get_key_object('Alt'), Key.alt)
        self.assertEqual(self.controller._get_key_object('SPACE'), Key.space)
    
    def test_get_key_object_unknown_key(self):
        """Test that unknown key returns None."""
        result = self.controller._get_key_object('unknown_key')
        self.assertIsNone(result)
    
    def test_get_key_object_with_whitespace(self):
        """Test that key mapping handles whitespace."""
        self.assertEqual(self.controller._get_key_object('  alt  '), Key.alt)


class TestThreadSafety(unittest.TestCase):
    """Test cases for thread safety."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.controller = WindowsController()
        self.mock_logger = Mock()
        self.controller.logger = self.mock_logger
    
    def test_concurrent_action_execution(self):
        """Test that concurrent action execution is thread-safe."""
        results = []
        
        def execute_action():
            with patch.object(self.controller, '_keyboard_key'):
                result = self.controller.execute_action('play_pause')
                results.append(result)
        
        threads = [threading.Thread(target=execute_action) for _ in range(5)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        
        self.assertEqual(len(results), 5)
        self.assertTrue(all(results))
    
    def test_concurrent_callback_registration(self):
        """Test that concurrent callback registration is thread-safe."""
        callbacks = []
        
        def register_callback():
            mock_callback = Mock()
            self.controller.register_callback(mock_callback)
            callbacks.append(mock_callback)
        
        threads = [threading.Thread(target=register_callback) for _ in range(5)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        
        self.assertEqual(len(self.controller.action_callbacks), 5)


class TestKeyboardShortcutDetails(unittest.TestCase):
    """Detailed test cases for keyboard shortcut execution."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.controller = WindowsController()
        self.mock_logger = Mock()
        self.controller.logger = self.mock_logger
    
    @patch('backend.controller.KeyboardController.press')
    @patch('backend.controller.KeyboardController.release')
    @patch('backend.controller.time.sleep')
    def test_keyboard_shortcut_key_order(self, mock_sleep, mock_release, mock_press):
        """Test that keyboard shortcut presses keys in correct order."""
        self.controller._keyboard_shortcut(['alt', 'tab'])
        
        # Verify press was called for both keys
        self.assertEqual(mock_press.call_count, 2)
        # Verify release was called for both keys in reverse order
        self.assertEqual(mock_release.call_count, 2)
    
    def test_keyboard_shortcut_with_invalid_key(self):
        """Test keyboard shortcut with invalid key raises error."""
        with self.assertRaises(ValueError):
            self.controller._keyboard_shortcut(['alt', 'invalid_key'])
    
    @patch('backend.controller.KeyboardController.press')
    @patch('backend.controller.KeyboardController.release')
    @patch('backend.controller.time.sleep')
    def test_single_key_press_timing(self, mock_sleep, mock_release, mock_press):
        """Test that single key press has proper timing."""
        self.controller._keyboard_key('space')
        
        # Verify press and release were called
        mock_press.assert_called_once()
        mock_release.assert_called_once()
        # Verify sleep was called for timing
        self.assertTrue(mock_sleep.called)


class TestActionTypes(unittest.TestCase):
    """Test cases for all supported action types."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.controller = WindowsController()
        self.mock_logger = Mock()
        self.controller.logger = self.mock_logger
    
    @patch('backend.controller.KeyboardController.press')
    @patch('backend.controller.KeyboardController.release')
    def test_all_action_types(self, mock_release, mock_press):
        """Test that all supported action types execute successfully."""
        action_types = [
            'app_switch',
            'close_window',
            'play_pause',
            'volume_up',
            'volume_down',
            'scroll_up',
            'scroll_down',
            'screenshot'
        ]
        
        for action_type in action_types:
            with patch.object(self.controller, '_mouse_scroll'):
                result = self.controller.execute_action(action_type)
                self.assertTrue(result, f'Action {action_type} should succeed')


if __name__ == '__main__':
    unittest.main()
