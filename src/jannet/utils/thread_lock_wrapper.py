from src.jannet.managers.db_manager import get_db_lock, get_vdb_lock
from functools import wraps


def db_locked(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        lock = get_db_lock()
        with lock:
            return func(*args, **kwargs)

    return wrapper


def vdb_locked(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        lock = get_vdb_lock()
        with lock:
            return func(*args, **kwargs)

    return wrapper
