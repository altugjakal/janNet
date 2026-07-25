import traceback
from time import sleep

from src.jannet.core.crawl import Crawl
from src.jannet.managers.db_manager import get_db
from src.jannet.utils.config import Config


def crawl(thread_id, vdb, rc):

    db = get_db()

    crawler = Crawl(sleep_median=Config.SLEEP_M, sleep_padding=Config.SLEEP_P, db=db, vdb=vdb, rc=rc,
                    thread_id=thread_id)

    if db.get_queue_size(thread_id=thread_id) == 0:
        db.add_to_queue_batch([(hash(url) % (10 ** 9), url) for url in Config.SEED_URLS[thread_id]], thread_id)

    crawl_count = 0

    while crawl_count < Config.MAX_CRAWLS:
        try:
            queue = db.get_queue_next(thread_id=thread_id)

            if len(queue) == 0:
                print("Crawled all, sleeping...")
                sleep(10)
                continue

            url = queue[0]
            id = queue[1]

            crawler.crawl(url, id)
            crawl_count += 1

        except Exception:
            print(f"[crawl thread={thread_id}] Exception:")
            traceback.print_exc()
            sleep(5)

    print(f"[crawl thread={thread_id}] Crawl queue cleared, completed iterations: {crawl_count}")