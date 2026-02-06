

import threading

_local = threading.local()
_db_lock = threading.Lock()

def get_vdb():
    if not hasattr(_local, 'vdb'):
        from core.db.vector_db import VectorDB
        _local.vdb = VectorDB()
    return _local.vdb

def get_db():
    if not hasattr(_local, 'db'):
        from core.db.index_db import IndexDB
        _local.db = IndexDB()
    return _local.db

def get_db_lock():
    return _db_lock