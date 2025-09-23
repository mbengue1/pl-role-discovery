"""
logging utility module for the premier league player role discovery app.

this module provides a centralized logging configuration for the entire application,
with support for different log levels and output formats.
"""

import logging
import os
import sys
from datetime import datetime
from pathlib import Path

# create logs directory if it doesn't exist
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

# configure log file name with timestamp
LOG_FILE = LOG_DIR / f"app_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

# define log format
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

def get_logger(name: str) -> logging.Logger:
    """
    create and return a logger with the specified name.
    
    args:
        name: the name of the logger, typically __name__ of the calling module
        
    returns:
        a configured logger instance
    """
    logger = logging.getLogger(name)
    
    # avoid adding handlers if they already exist
    if logger.hasHandlers():
        return logger
    
    # set log level from environment variable or default to INFO
    log_level_name = os.environ.get("LOG_LEVEL", "INFO").upper()
    log_level = getattr(logging, log_level_name, logging.INFO)
    logger.setLevel(log_level)
    
    # create file handler
    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
    logger.addHandler(file_handler)
    
    # create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
    logger.addHandler(console_handler)
    
    return logger
