import logging
from time import sleep

from src.jannet.core.crawl import Crawl
from src.jannet.utils.config import Config

logger = logging.getLogger(__name__)


def crawl(thread_id, vdb, rc, db):

    crawler = Crawl(
        sleep_median=Config.SLEEP_M,
        sleep_padding=Config.SLEEP_P,
        db=db,
        vdb=vdb,
        rc=rc,
        thread_id=thread_id
    )


    if db.get_queue_size(thread_id=thread_id) == 0:

        db.add_to_queue_batch(
            [(hash(url) % (10 ** 9), url) for url in Config.SEED_URLS[thread_id]],
            thread_id
        )

    crawl_count = 0

    while crawl_count < Config.MAX_CRAWLS:
        try:
            queue = db.get_queue_next(thread_id=thread_id)

            if len(queue) == 0:
                logger.info("Thread %d: crawl queue empty, sleeping", thread_id)
                sleep(10)
                continue

            url = queue[0]
            id = queue[1]


            is_crawled = crawler.crawl(url, id)

            if is_crawled:
                crawl_count += 1

        except Exception:
            logger.exception("Thread %d: crawler iteration failed", thread_id)
            sleep(5)

    logger.info(
        "Thread %d: crawl completed after %d iterations",
        thread_id,
        crawl_count
    )