

import threading

from utils.config import Config

_local = threading.local()
_db_lock = threading.Lock()

def get_vdb():
    if not hasattr(_local, 'vdb'):
        from core.db.vector_db import VectorDB
        _local.vdb = VectorDB()
    return _local.vdb

def get_db():
    if not hasattr(_local, 'index'):
        from core.db.index_db import IndexDB
        _local.db = IndexDB(host=Config.DB_HOST, user=Config.DB_USER, password=Config.DB_PASSWORD, database=Config.DB_DATABASE)
    return _local.db

def get_db_lock():
    return _db_lock