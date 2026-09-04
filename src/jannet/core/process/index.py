import gc
import hashlib
import logging
import random
import time
from collections import defaultdict
from urllib.parse import urljoin

from lxml import html

from src.jannet.core.process.reverse_index import ReverseIndexCommunicator
from src.jannet.utils.config import Config
from src.jannet.utils.misc import extract_words
from src.jannet.utils.parsing import extract_anchors, html_to_clean

logger = logging.getLogger(__name__)

class Index:
    def __init__(self, db, vdb):
        self.db = db
        self.vdb = vdb
        self.ri_client = ReverseIndexCommunicator()

    def assign_importance_by_location(self, element_type: str) -> int:
        base_importance = Config.HTML_IMPORTANCE_MAP.get(element_type, Config.HTML_DEFAULT_WEIGHT)
        return base_importance

    def process(self, url: str, content: str, id: int) -> bool:

        t0 = time.perf_counter()

        t1 = time.perf_counter()
        anchors, anchor_values = extract_anchors(content)

        to_be_queued = set()
        to_be_graphed = set()
        new_count = 0
        for anchor, a_v in zip(anchors, anchor_values):
            absolute_url = urljoin(url, anchor)
            absolute_url = absolute_url.rstrip("/")
            absolute_url = absolute_url.split("#")[0]
            new_url_id = int.from_bytes(hashlib.md5(absolute_url.encode()).digest(), 'big') % 10**9

            for value in extract_words(a_v):
                pass

            if not absolute_url.startswith(("http://", "https://")):
                continue

            if absolute_url.endswith(Config.DESIGN_FILE_EXTS):
                continue

            to_be_queued.add((new_url_id, absolute_url))
            to_be_graphed.add((id, new_url_id))
            new_count += 1
        logger.info("Parse anchors: %.3fs", time.perf_counter() - t1)

        t2 = time.perf_counter()
        self.db.add_link_relation_batch(to_be_graphed)
        logger.info("add_link_relation_batch: %.3fs", time.perf_counter() - t2)

        t3 = time.perf_counter()
        self.db.add_to_queue_batch(to_be_queued, thread_id=(random.randrange(0, Config.CRAWL_THREAD_COUNT)))
        logger.info("add_to_queue_batch (%d urls): %.3fs", new_count, time.perf_counter() - t3)

        if new_count > 0:
            logger.info("Queued %d new URLs", new_count)

        t4 = time.perf_counter()

        root = html.fromstring(content)

        token_map = defaultdict(list)
        pos_length = 0

        for i, e in enumerate(root.iter()):
            text_content = e.text if e.text else ""
            if not text_content.strip():
                continue
            text_content = text_content.lower()

            importance = self.assign_importance_by_location(e.tag)
            for j, token in enumerate(text_content.split(" ")):
                hit = (importance, pos_length + j)
                token_map[token].append(hit)

            pos_length += len(e.text.split(" "))

        self.ri_client.insert(id, token_map)
        logger.info("HTML parse & reverse index insertion: %.3fs", time.perf_counter() - t4)

        t5 = time.perf_counter()
        clean_content = html_to_clean(content)
        logger.info("html_to_clean: %.3fs", time.perf_counter() - t5)

        words = clean_content.split()
        id_emb_pairs = set()
        t6 = time.perf_counter()
        for i in range(0, len(words), 400):
            chunk = ' '.join(words[i:i + 400])
            combined_string = f"{id}:{i}"
            chunk_id = int.from_bytes(hashlib.md5(combined_string.encode('utf-8')).digest(), byteorder='big') % (10 ** 9)
            self.vdb.insert(text=chunk, id=chunk_id)
            del chunk
            del combined_string
            if i % 40000 == 0:
                gc.collect()

            id_emb_pairs.add((id, chunk_id))  #use doc id
        logger.info("VDB chunk insert (%d chunks): %.3fs", len(id_emb_pairs), time.perf_counter() - t6)

        t7 = time.perf_counter()
        self.db.manage_vector_for_index_batch(list(id_emb_pairs))
        logger.info("manage_vector_for_index_batch: %.3fs", time.perf_counter() - t7)

        self.db.mark_url_as_processed(id)

        logger.info("TOTAL process: %.3fs", time.perf_counter() - t0)

        return True