import logging
from functools import wraps

# Configure logging
def setup_logger():
    logger = logging.getLogger("AppLogger")
    logger.setLevel(logging.DEBUG)

    # Create console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # Create file handler
    fh = logging.FileHandler("app_debug.log")
    fh.setLevel(logging.DEBUG)

    # Define log format
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)

    # Add handlers to logger
    logger.addHandler(ch)
    logger.addHandler(fh)

    return logger

# Initialize logger
logger = setup_logger()

# Decorator for logging function calls
def log_function_call(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.debug(f"Calling function: {func.__name__} with args: {args} and kwargs: {kwargs}")
        try:
            result = func(*args, **kwargs)
            logger.debug(f"Function {func.__name__} returned: {result}")
            return result
        except Exception as e:
            logger.error(f"Error in function {func.__name__}: {e}")
            raise
    return wrapper

import logging
from functools import wraps

# Configure logging
def setup_logger():
    logger = logging.getLogger("AppLogger")
    logger.setLevel(logging.DEBUG)

    # Create console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # Create file handler
    fh = logging.FileHandler("app_debug.log")
    fh.setLevel(logging.DEBUG)

    # Define log format
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)

    # Add handlers to logger
    logger.addHandler(ch)
    logger.addHandler(fh)

    return logger

# Initialize logger
logger = setup_logger()

# Decorator for logging function calls
def log_function_call(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.debug(f"Calling function: {func.__name__} with args: {args} and kwargs: {kwargs}")
        try:
            result = func(*args, **kwargs)
            logger.debug(f"Function {func.__name__} returned: {result}")
            return result
        except Exception as e:
            logger.error(f"Error in function {func.__name__}: {e}")
            raise
    return wrapper