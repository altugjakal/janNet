from core.vectordb.vectordb import VectorDB

_db = None

def get_db():
    global _db
    if _db is None:
        _db = VectorDB()
        return _db
    else:
        return _db