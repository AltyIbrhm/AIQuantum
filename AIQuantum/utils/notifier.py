import logging
from typing import Optional

class Notifier:
    """A simple notification system for logging and alerts."""
    
    def __init__(self, name: str = "AIQuantum"):
        """Initialize the notifier with a logger name."""
        self.logger = logging.getLogger(name)
        self._setup_logger()
        
    def _setup_logger(self):
        """Set up the logger with basic configuration."""
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    def info(self, message: str, **kwargs):
        """Log an info message."""
        self.logger.info(message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log a warning message."""
        self.logger.warning(message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log an error message."""
        self.logger.error(message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log a critical message."""
        self.logger.critical(message, **kwargs)
    
    def debug(self, message: str, **kwargs):
        """Log a debug message."""
        self.logger.debug(message, **kwargs)
    
    def notify(self, message: str, level: str = "info", **kwargs):
        """Send a notification with the specified level."""
        method = getattr(self, level.lower(), self.info)
        method(message, **kwargs) 