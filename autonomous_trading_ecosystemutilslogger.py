"""
Robust logging system with Firebase integration for critical events.
"""
import logging
import sys
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum

class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class TradingLogger:
    def __init__(self, name: str = "trading_ecosystem", firestore_client=None):
        self.name = name
        self.firestore_client = firestore_client
        self.logger = self._setup_logger()
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _setup_logger(self) -> logging.Logger:
        """Configure logger with appropriate handlers and formatting."""
        logger = logging.getLogger(self.name)
        logger.setLevel(logging.DEBUG)
        
        # Prevent duplicate handlers
        if logger.handlers:
            return logger
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_format)
        console_handler.setLevel(logging.INFO)
        
        # File handler for error logs
        file_handler = logging.FileHandler(f'logs/trading_{self.session_id}.log')
        file_format = logging