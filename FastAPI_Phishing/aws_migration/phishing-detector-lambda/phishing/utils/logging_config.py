import logging
import time
from functools import wraps

# Configure logging for Lambda
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def log_duration(func):
    """
    Decorator to log function execution duration
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        logger = logging.getLogger(func.__name__)
        
        try:
            logger.info(f"Starting {func.__name__}")
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            logger.info(f"Completed {func.__name__} in {duration:.2f} seconds")
            return result
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Error in {func.__name__} after {duration:.2f} seconds: {str(e)}")
            raise
    
    return wrapper