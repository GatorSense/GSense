# logging.py
import logging
from datetime import datetime

def setup_logger():
    logger = logging.getLogger("GSenseLogger")
    logger.setLevel(logging.DEBUG)
    
    # Create a file handler for writing logs
    handler = logging.FileHandler(f"logs/gsense_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    handler.setLevel(logging.DEBUG)

    # Create a formatter and set it for the handler
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(handler)

    return logger

# Initialize the logger
logger = setup_logger()
