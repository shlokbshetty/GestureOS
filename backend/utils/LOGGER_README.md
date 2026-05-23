# Structured Logging System

## Overview

The structured logging system provides centralized, production-grade logging for the Gesture Control Desktop Application. It features:

- **Rotating File Handler**: Automatically rotates log files when they exceed 10MB, keeping the last 5 backup files
- **Structured Format**: Consistent log format with timestamps, severity levels, component names, and messages
- **Dual Output**: Logs to both file and console for development and production use
- **Thread-Safe**: Safe for concurrent logging from multiple threads
- **Singleton Pattern**: Single logger instance shared across the application
- **Component-Based**: Each module gets its own logger with a component name

## Configuration

### File Rotation Settings

- **Max File Size**: 10MB per log file
- **Backup Files**: 5 rotated files kept (app.log.1, app.log.2, etc.)
- **Log Directory**: `logs/` (created automatically)
- **Log File**: `logs/app.log`

### Log Format

```
YYYY-MM-DD HH:MM:SS - COMPONENT_NAME - LEVEL - message
```

Example:
```
2026-05-23 18:37:57 - gesture_engine - INFO - Gesture detected: app_switch
2026-05-23 18:37:57 - controller - ERROR - Failed to execute action: Alt+Tab
```

## Usage

### Basic Usage

```python
from backend.utils import get_logger

# Get a logger for your component
logger = get_logger('my_component')

# Log messages at different levels
logger.debug('Debug information')
logger.info('Informational message')
logger.warning('Warning message')
logger.error('Error message')
```

### Application Startup

```python
from backend.utils import initialize_logging

# Call once at application startup
initialize_logging()
```

### Application Shutdown

```python
from backend.utils import shutdown_logging

# Call during graceful shutdown
shutdown_logging()
```

### Complete Example

```python
from backend.utils import get_logger, initialize_logging, shutdown_logging

def main():
    # Initialize logging
    initialize_logging()
    
    # Get logger for this module
    logger = get_logger('main')
    
    try:
        logger.info('Application started')
        # Your application code here
        logger.info('Application completed successfully')
    except Exception as e:
        logger.error(f'Application failed: {str(e)}')
    finally:
        # Shutdown logging
        shutdown_logging()

if __name__ == '__main__':
    main()
```

## Component Loggers

Each component should get its own logger with a descriptive name:

```python
# In gesture_engine.py
logger = get_logger('gesture_engine')

# In controller.py
logger = get_logger('controller')

# In state_manager.py
logger = get_logger('state_manager')

# In api_server.py
logger = get_logger('api_server')
```

## Log Levels

| Level | Usage | Example |
|-------|-------|---------|
| DEBUG | Detailed diagnostic information | Frame processing details, variable values |
| INFO | General informational messages | Application startup, gesture detected |
| WARNING | Warning messages for potential issues | Low frame rate, high latency |
| ERROR | Error messages for failures | Camera disconnected, action failed |

## Log Rotation

The logging system automatically rotates log files when they exceed 10MB:

1. Current log file: `logs/app.log`
2. When size exceeds 10MB, it's renamed to `logs/app.log.1`
3. Previous backups are renamed: `app.log.1` → `app.log.2`, etc.
4. Old backups beyond the 5-file limit are deleted

This ensures log files don't consume excessive disk space while maintaining a history of recent logs.

## Thread Safety

The logging system is thread-safe and can be used from multiple threads concurrently:

```python
import threading
from backend.utils import get_logger

logger = get_logger('my_component')

def worker(thread_id):
    logger.info(f'Thread {thread_id} started')
    # Do work
    logger.info(f'Thread {thread_id} completed')

# Safe to log from multiple threads
threads = [threading.Thread(target=worker, args=(i,)) for i in range(5)]
for thread in threads:
    thread.start()
for thread in threads:
    thread.join()
```

## Testing

Run the test suite to verify the logging system:

```bash
python -m unittest backend.utils.test_logger -v
```

Tests verify:
- Singleton pattern
- File rotation configuration
- Log format
- Component-specific loggers
- Thread safety
- Graceful shutdown

## Performance

The logging system is optimized for performance:

- **File I/O**: Buffered writes to minimize disk I/O
- **Formatting**: Efficient string formatting
- **Thread Safety**: Uses Python's built-in thread-safe logging
- **Memory**: Minimal memory overhead

## Troubleshooting

### Logs not appearing in file

1. Check that the `logs/` directory exists and is writable
2. Verify that `initialize_logging()` was called
3. Check file permissions

### Log file growing too large

The log file should automatically rotate at 10MB. If it doesn't:

1. Verify the `maxBytes` setting is 10MB (10 * 1024 * 1024)
2. Check that the `backupCount` is set to 5
3. Ensure the logs directory has sufficient disk space

### Unicode/Encoding issues

The logger handles Unicode characters. If you see encoding errors:

1. Ensure your Python environment is set to UTF-8
2. Use the logger's built-in encoding handling

## Integration with Application

The logger should be initialized early in the application startup:

```python
# main.py
from backend.utils import initialize_logging, shutdown_logging
import signal

def signal_handler(sig, frame):
    shutdown_logging()
    exit(0)

if __name__ == '__main__':
    initialize_logging()
    signal.signal(signal.SIGINT, signal_handler)
    
    # Start application
    app.run()
```

## Future Enhancements

Potential improvements for the logging system:

- Log filtering by component or level
- Remote logging to centralized server
- Structured JSON logging for log aggregation
- Performance metrics logging
- Custom log handlers for specific components
