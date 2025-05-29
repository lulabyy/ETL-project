"""
helpers_logger.py

This module provides a utility function to initialize and configure a logger for the application.
It ensures that logs are written both to a specified log file and to the console, using a consistent and detailed format.

Functionality:
- initLogger: Creates and configures a logger instance with a given name, output directory, and filename.
  The logger writes logs to both file and standard output, with formatting that includes timestamps, log level,
  module/function/line and message details.

Typical usage:
- Used at the start of main scripts (such as main_streamlit.py and main_etl.py) to set up centralized logging.
- Ensures logs are persisted for troubleshooting and monitoring, and visible in real time during execution.

This module should be imported and used within other parts of the portfolio analytics application.
It is not intended to be executed directly.

See main_streamlit.py and main_etl.py for examples of logger initialization and usage.
"""

import logging
import os

def initLogger(log_name: str, log_dir_path: str, log_filename: str) -> logging.Logger:
    """
    Initialize the logger and write the logs to the specified folder.

    Args:
        log_name (str): Name for the logger instance.
        log_dir_path (str): Path to the directory where logs will be stored.
        log_filename (str): Name of the log file.

    Returns:
        logging.Logger: The initialized logger instance.
    """
    os.makedirs(log_dir_path, exist_ok=True)

    log_file = os.path.join(log_dir_path, log_filename)

    # Création du logger si il existe pas déjà
    logger = logging.getLogger(log_name)
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            "%(asctime)s | %(name)s | %(levelname)s | %(module)s | %(funcName)s | %(lineno)d | %(message)s"
        )

        file_handler = logging.FileHandler(log_file, mode="w", encoding="utf-8")
        file_handler.setFormatter(formatter)
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)

    return logger
