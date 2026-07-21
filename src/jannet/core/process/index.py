import random
import time
from collections import defaultdict
from urllib.parse import urljoin

from lxml import html

from src.jannet.core.process.reverse_index import ReverseIndexCommunicator
from src.jannet.utils.config import Config
from src.jannet.utils.misc import extract_words
from src.jannet.utils.parsing import extract_anchors, html_to_clean


class Index:
    def __init__(self, db, vdb):
        self.db = db
        self.vdb = vdb
        self.ri_client = ReverseIndexCommunicator()

    def assign_importance_by_location(self, element_type):
        base_importance = Config.HTML_IMPORTANCE_MAP.get(element_type, Config.HTML_DEFAULT_WEIGHT)
        return base_importance

    def process(self, url, content, id):
        self.db.mark_url_as_processed(id)
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
            new_url_id = hash(absolute_url) % (10 ** 9)

            for value in extract_words(a_v):
                pass

            if not absolute_url.startswith(("http://", "https://")):
                continue

            if absolute_url.endswith(Config.DESIGN_FILE_EXTS):
                continue

            to_be_queued.add((new_url_id, absolute_url))
            to_be_graphed.add((id, new_url_id))
            new_count += 1
        print(f"[TIMER] parse anchors: {time.perf_counter() - t1:.3f}s")

        t2 = time.perf_counter()
        self.db.add_link_relation_batch(to_be_graphed)
        print(f"[TIMER] add_link_relation_batch: {time.perf_counter() - t2:.3f}s")

        t3 = time.perf_counter()
        self.db.add_to_queue_batch(to_be_queued, thread_id=(random.randrange(0, Config.CRAWL_THREAD_COUNT)))
        print(f"[TIMER] add_to_queue_batch ({new_count} urls): {time.perf_counter() - t3:.3f}s")

        if new_count > 0:
            print(f"  → Queued {new_count} new URLs")

        t4 = time.perf_counter()
        recapitalised_content = content.lower()
        root = html.fromstring(recapitalised_content)

        token_map = defaultdict(list)
        pos_length = 0

        for i, e in enumerate(root.iter()):
            text_content = e.text if e.text else ""
            if not text_content.strip():
                continue

            importance = self.assign_importance_by_location(e.tag)
            for j, token in enumerate(text_content.split(" ")):
                hit = (importance, pos_length + j)
                token_map[token].append(hit)

            pos_length += len(e.text.split(" "))

        self.ri_client.insert(id, token_map)
        print(f"[TIMER] html parse & reverse index insertion: {time.perf_counter() - t4:.3f}s")

        t5 = time.perf_counter()
        clean_content = html_to_clean(content)
        print(f"[TIMER] html_to_clean: {time.perf_counter() - t5:.3f}s")

        words = clean_content.split()
        url_emb_pairs = set()
        t6 = time.perf_counter()
        for i in range(0, len(words), 400):
            chunk = ' '.join(words[i:i + 400])
            chunk_id = hash((url, i)) % (10 ** 9)
            self.vdb.insert(text=chunk, id=chunk_id)
            url_emb_pairs.add((chunk_id, url))
        print(f"[TIMER] vdb chunk insert ({len(url_emb_pairs)} chunks): {time.perf_counter() - t6:.3f}s")

        t7 = time.perf_counter()
        self.db.manage_vector_for_index_batch(list(url_emb_pairs))
        print(f"[TIMER] manage_vector_for_index_batch: {time.perf_counter() - t7:.3f}s")

        print(f"[TIMER] TOTAL process: {time.perf_counter() - t0:.3f}s")