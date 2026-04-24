"""
Logging configuration for the Social Security analysis application.

Provides structured logging with file and console handlers,
enabling audit trails for data loading and processing errors.
"""

import logging
import os
from datetime import datetime


# Configure logging with both file and console handlers
def configure_logging(log_dir: str = "logs") -> logging.Logger:
    """
    Configure and return the main logger for the application.
    
    Args:
        log_dir: Directory to store log files (created if not exists)
        
    Returns:
        Configured logger instance
    """
    # Create logs directory if it doesn't exist
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Create logger
    logger = logging.getLogger("social_sec_analysis")
    logger.setLevel(logging.DEBUG)
    
    # Clear any existing handlers to avoid duplicates
    logger.handlers = []
    
    # Create file handler with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"social_sec_analysis_{timestamp}.log")
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Create formatter
    detailed_formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)-8s [%(name)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        '%(levelname)-8s: %(message)s'
    )
    
    file_handler.setFormatter(detailed_formatter)
    console_handler.setFormatter(simple_formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


# Get the configured logger instance
logger = configure_logging()


def log_file_loaded(filename: str, record_count: int = None) -> None:
    """Log successful file loading."""
    if record_count is not None:
        logger.info(f"Successfully loaded '{filename}' with {record_count} records")
    else:
        logger.info(f"Successfully loaded '{filename}'")


def log_validation_error(filename: str, error_message: str) -> None:
    """Log validation error during file loading."""
    logger.error(f"Validation error in '{filename}': {error_message}")


def log_file_error(filename: str, error_message: str) -> None:
    """Log file access or parsing error."""
    logger.error(f"Error loading '{filename}': {error_message}")


def log_data_check(check_name: str, status: str, details: str = None) -> None:
    """Log data validation check result."""
    message = f"Data check '{check_name}': {status}"
    if details:
        message += f" ({details})"
    logger.info(message)


def log_scenario_start(scenario_name: str, start_date: str) -> None:
    """Log start of scenario processing."""
    logger.info(f"Starting scenario: '{scenario_name}' with start date: {start_date}")


def log_scenario_complete(scenario_name: str) -> None:
    """Log completion of scenario processing."""
    logger.info(f"Completed scenario: '{scenario_name}'")


def log_report_generated(filename: str, sheet_count: int = None) -> None:
    """Log successful report generation."""
    if sheet_count is not None:
        logger.info(f"Generated report '{filename}' with {sheet_count} sheets")
    else:
        logger.info(f"Generated report '{filename}'")
