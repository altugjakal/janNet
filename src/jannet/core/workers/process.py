import logging
from time import sleep

from src.jannet.core.process.index import Index
from src.jannet.utils.config import Config

logger = logging.getLogger(__name__)


def process(vdb, db, pc):

    indexer = Index(db=db, vdb=vdb)

    process_count = 0

    while process_count < Config.MAX_PROCESS:
        try:
            queue = pc.get()

            if not queue:
                logger.info("Process queue empty, sleeping")
                sleep(10)
                continue

            url = queue[0]
            content = queue[1]
            doc_id = queue[2]

            logger.info("Processing %s", url)

            indexer.process(url, content, doc_id)
            process_count += 1

        except Exception:
            logger.exception("Processing iteration failed")
            sleep(5)

    logger.info(
        "Process queue completed after %d iterations",
        process_count
    )