from core.db.vectordb import VectorDB
from core.db.index import IndexDB

_db = None
_vdb = None

def get_vdb():
    global _vdb
    if _vdb is None:
        _vdb = VectorDB()
        return _vdb
    else:
        return _vdb

def get_db():
    global _db
    if _db is None:
        _db = IndexDB()
        return _db
    else:
        return _db