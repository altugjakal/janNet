import time
from functools import wraps

def timed(func):
    @wraps(func)

    def wrapper(*args, **kwargs):
        t0 = time.time()
        result = func(*args, **kwargs)
        t1 = time.time()
        print("\n" + str(t1-t0), end=" - Time taken to run " + func.__name__ + "\n")
        return result
    return wrapper


