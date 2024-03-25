import logging
from logging.handlers import RotatingFileHandler
import os
import sys
from tkinter import messagebox
from datetime import datetime

class StreamToLogger(object):
    """
    Fake file-like stream object that redirects writes to a logger instance.
    """
    def __init__(self, logger, log_level=logging.INFO):
        self.logger = logger
        self.log_level = log_level
        self.linebuf = ''

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())

    def flush(self):
        pass

def init_logger(log_directory="logs", log_file_prefix="log"):
    """
    Initializes logging for the application, redirecting stdout and stderr to a log file
    with the current date and time in its name.
    
    Args:
        log_directory (str): Directory where log files will be stored.
        log_file_prefix (str): Prefix for the log file name.
    """
    # Ensure the log directory exists
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

    # Format the log file name with the current date and time
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file_name = f"{log_file_prefix}_{current_time}.log"
    log_file_path = os.path.join(log_directory, log_file_name)

    # Configure the logger
    logger = logging.getLogger("MyAppLogger")
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    file_handler = RotatingFileHandler(log_file_path, maxBytes=5*1024*1024, backupCount=5)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Redirect stdout and stderr to the logger
    sys.stdout = StreamToLogger(logger, logging.INFO)
    sys.stderr = StreamToLogger(logger, logging.ERROR)