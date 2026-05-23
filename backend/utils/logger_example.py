"""
Example usage of the structured logging system.

This module demonstrates how to use the logger in different components
of the gesture control application.
"""

from logger import get_logger, initialize_logging, shutdown_logging


def example_gesture_engine():
    """Example: Using logger in the gesture engine."""
    logger = get_logger('gesture_engine')
    
    logger.info('Gesture engine starting')
    logger.debug('Initializing camera')
    logger.info('Camera initialized successfully')
    logger.info('Gesture detected: app_switch with confidence 0.95')
    logger.warning('Frame rate dropped below 30 FPS')
    logger.error('Camera disconnected unexpectedly')


def example_controller():
    """Example: Using logger in the Windows controller."""
    logger = get_logger('controller')
    
    logger.info('Controller initialized')
    logger.info('Executing action: Alt+Tab')
    logger.debug('Keyboard shortcut sent successfully')
    logger.info('Action executed: app_switch')


def example_state_manager():
    """Example: Using logger in the state manager."""
    logger = get_logger('state_manager')
    
    logger.info('State transition: stopped -> starting')
    logger.info('State transition: starting -> running')
    logger.debug('Gesture engine started')
    logger.info('Application is now running')
    logger.info('State transition: running -> stopping')
    logger.info('State transition: stopping -> stopped')


def example_api_server():
    """Example: Using logger in the API server."""
    logger = get_logger('api_server')
    
    logger.info('API server starting on localhost:5000')
    logger.debug('FastAPI app initialized')
    logger.info('WebSocket endpoint registered at /ws')
    logger.info('API server ready to accept connections')
    logger.debug('Client connected: 127.0.0.1:54321')
    logger.info('Gesture event broadcasted to 3 clients')


def main():
    """Main example demonstrating logger usage."""
    # Initialize logging system
    initialize_logging()
    
    print("=" * 60)
    print("Gesture Control Application - Logging Example")
    print("=" * 60)
    print()
    
    # Run examples
    print("1. Gesture Engine Logging:")
    print("-" * 60)
    example_gesture_engine()
    print()
    
    print("2. Controller Logging:")
    print("-" * 60)
    example_controller()
    print()
    
    print("3. State Manager Logging:")
    print("-" * 60)
    example_state_manager()
    print()
    
    print("4. API Server Logging:")
    print("-" * 60)
    example_api_server()
    print()
    
    print("=" * 60)
    print("Log file created at: logs/app.log")
    print("=" * 60)
    
    # Shutdown logging system
    shutdown_logging()


if __name__ == '__main__':
    main()
