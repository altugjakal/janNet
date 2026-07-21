import time

from src.jannet.core.db.index_db import IndexDB
from src.jannet.utils.config import Config

db = IndexDB(host=Config.DB_HOST, user=Config.DB_USER, password=Config.DB_PASSWORD, database=Config.DB_DATABASE, port=Config.DB_PORT)
id_list = [23591813, 30380711]
t1 = time.perf_counter()
results = db.get_contents_by_ids(id_list)
t2 = time.perf_counter()
print(results)
print(t2 - t1)