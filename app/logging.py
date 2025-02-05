import logging
from datetime import datetime
from pathlib import Path

def setup_logger():
    # Create log directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(parents=True, exist_ok=True)  # Create the directory if it doesn't exist

    # Set up logger
    logger = logging.getLogger("GSenseLogger")
    logger.setLevel(logging.DEBUG)
    
    # Create a file handler for writing logs with a timestamped filename
    log_file = log_dir / f"gsense_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    handler = logging.FileHandler(log_file)
    handler.setLevel(logging.DEBUG)

    # Create a formatter and set it for the handler
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(handler)

    return logger

# Initialize the logger
logger = setup_logger()
