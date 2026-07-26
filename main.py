import concurrent

from concurrent.futures import ThreadPoolExecutor


from src.jannet.core.process.queuers.process_queuer import ProcessQueuer
from src.jannet.core.process.reverse_index import ReverseIndexCommunicator
from src.jannet.core.process.robots_cache import RobotsCache
from src.jannet.core.workers.crawl import crawl
from src.jannet.core.workers.process import process
from src.jannet.managers.db_manager import get_vdb, get_db
from src.jannet.utils.config import Config


vdb = get_vdb()
rc = RobotsCache(100)
db = get_db()
pc = ProcessQueuer(db)

if __name__ == "__main__":

    ri_client = ReverseIndexCommunicator()
    datalist = []
    with ThreadPoolExecutor() as exe:
        futures = []
        for t_id in range(Config.CRAWL_THREAD_COUNT):
            futures.append(exe.submit(crawl, t_id, vdb, rc, db))
        for _ in range(Config.PROCESS_THREAD_COUNT):
            futures.append(exe.submit(process, vdb, db, pc))



        concurrent.futures.wait(futures)
        for f in futures: datalist.append(f.result())


    vdb.save_to_disk()
    ri_client.commit()

