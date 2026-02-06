from managers.db_manager import get_db_lock
from functools import wraps

def locked(func):
    @wraps(func)

    def wrapper(*args, **kwargs):
        lock = get_db_lock()
        with lock:
            return func(*args, **kwargs)
    return wrapper

