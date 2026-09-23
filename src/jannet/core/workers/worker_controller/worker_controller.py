import concurrent
from concurrent.futures import ThreadPoolExecutor

from src.jannet.core.process.queuers.process_queuer import ProcessQueuer
from src.jannet.core.process.reverse_index import ReverseIndexCommunicator
from src.jannet.core.process.robots_cache import RobotsCache
from src.jannet.core.workers.crawl import crawl
from src.jannet.core.workers.process import process
from src.jannet.utils.config import Config


class WorkerController:
    def __init__(self, db, vdb):
        self.pc = ProcessQueuer(db)
        self.ri_client = ReverseIndexCommunicator()
        self.db = db
        self.vdb = vdb
        self.rc = RobotsCache(100)
        self.process_futures = []
        self.crawl_futures = []
        self.crawl_thread_pool_executor = ThreadPoolExecutor(Config.CRAWL_THREAD_COUNT)
        self.process_thread_pool_executor = ThreadPoolExecutor(Config.PROCESS_THREAD_COUNT)


    def start_process_workers(self):
        with self.process_thread_pool_executor as exe:
            for _ in range(Config.PROCESS_THREAD_COUNT):
                self.crawl_futures.append(exe.submit(process, self.vdb, self.db, self.pc))

            concurrent.futures.wait(self.process_futures)
            self.stop_crawl_workers()


    def start_crawl_workers(self):
        with self.crawl_thread_pool_executor as exe:
            for t_id in range(Config.CRAWL_THREAD_COUNT):
                self.process_futures.append(exe.submit(crawl, t_id, self.vdb, self.rc, self.db))

                concurrent.futures.wait(self.crawl_futures)
                self.stop_crawl_workers()

    def stop_process_workers(self):

        return_list = []
        with self.process_thread_pool_executor as exe:
            exe.shutdown()

        for f in self.process_futures: return_list.append(f.result())

        self.vdb.save_to_disk()
        self.ri_client.commit()

    def stop_crawl_workers(self):

        return_list = []
        with self.crawl_thread_pool_executor as exe:
            exe.shutdown()

        for f in self.crawl_futures: return_list.append(f.result())


