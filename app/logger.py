import sys
from datetime import datetime
from loguru import logger as _logger
from app.config import PROJECT_ROOT

_print_level = "INFO"
_log_callbacks = []

def add_log_callback(callback):
    """Register a callback to receive log messages"""
    _log_callbacks.append(callback)
    return len(_log_callbacks) - 1  # Return index as ID

def remove_log_callback(callback_id):
    """Remove a callback by its ID"""
    if 0 <= callback_id < len(_log_callbacks):
        _log_callbacks[callback_id] = None

def define_log_level(print_level="INFO", logfile_level="DEBUG", name: str = None):
    """Adjust the log level to above level"""
    global _print_level
    _print_level = print_level

    current_date = datetime.now()
    formatted_date = current_date.strftime("%Y%m%d%H%M%S")
    log_name = (
        f"{name}_{formatted_date}" if name else formatted_date
    )  # name a log with prefix name

    # Make sure to remove only if handlers exist
    try:
        _logger.remove()
    except ValueError:
        pass  # No handlers to remove, that's okay

    _logger.add(sys.stderr, level=print_level)
    _logger.add(PROJECT_ROOT / f"logs/{log_name}.log", level=logfile_level)

    return _logger

# Intercept function for the logger
def _intercept_message(record):
    message = record["message"]
    # Call all registered callbacks
    for callback in _log_callbacks:
        if callback:  # Skip None callbacks (removed ones)
            callback(message)
    return record

# Create the logger instance
logger = define_log_level()

# Apply the interception to capture messages
logger = logger.patch(_intercept_message)

if __name__ == "__main__":
    logger.info("Starting application")
    logger.debug("Debug message")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.critical("Critical message")

    try:
        raise ValueError("Test error")
    except Exception as e:
        logger.exception(f"An error occurred: {e}")
