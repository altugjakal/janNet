import logging
import time
from functools import wraps

logger = logging.getLogger(__name__)

def timed(func):
    @wraps(func)

    def wrapper(*args, **kwargs):
        t0 = time.time()
        result = func(*args, **kwargs)
        t1 = time.time()
        logger.info("\n" + str(t1-t0), end=" - Time taken to run " + func.__name__ + "\n")
        return result
    return wrapper


