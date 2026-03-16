import random
import time
from collections import defaultdict, Counter
from urllib.parse import urljoin

from math import log1p

from src.jannet.utils.config import Config
from src.jannet.utils.misc import extract_words
from src.jannet.utils.parsing import extract_anchors, reformat_html_tags, html_to_clean


class Index:
    def __init__(self, db, vdb):
        self.db = db
        self.vdb = vdb

    def assign_importance_by_location(self, element_type):
        base_importance = Config.HTML_IMPORTANCE_MAP.get(element_type, 1)
        return base_importance

    def process(self, url, content, id):

        self.db.mark_url_as_processed(id)
        t0 = time.perf_counter()

        anchors, anchor_values = extract_anchors(content)

        to_be_queued = set()
        to_be_graphed = set()
        new_count = 0
        tuples = []
        for anchor, a_v in zip(anchors, anchor_values):
            absolute_url = urljoin(url, anchor)
            absolute_url = absolute_url.rstrip("/")
            absolute_url = absolute_url.split("#")[0]

            for value in extract_words(a_v):
                tuples.append((absolute_url, value, Config.HTML_IMPORTANCE_MAP.get("h1")))
                tuples.append((url, value, Config.HTML_IMPORTANCE_MAP.get("p")))

            if not absolute_url.startswith(("http://", "https://")):
                continue

            if absolute_url.endswith(Config.DESIGN_FILE_EXTS):
                continue

            to_id = hash(absolute_url) % (10 ** 9)
            to_be_queued.add((to_id, absolute_url))
            to_be_graphed.add((to_id, id))
            new_count += 1

        t1 = time.perf_counter()
        self.db.add_link_relation_batch(to_be_graphed)
        print(f"[TIMER] add_link_relation_batch: {time.perf_counter() - t1:.3f}s")

        t2 = time.perf_counter()
        self.db.manage_for_index_batch(tuples)
        print(f"[TIMER] manage_for_index_batch: {time.perf_counter() - t2:.3f}s")

        t3 = time.perf_counter()
        self.db.add_to_queue_batch(to_be_queued, thread_id=(random.randrange(0, Config.THREAD_COUNT)))
        print(f"[TIMER] add_to_queue_batch ({new_count} urls): {time.perf_counter() - t3:.3f}s")

        if new_count > 0:
            print(f"  → Queued {new_count} new URLs")

        t4 = time.perf_counter()
        page_contents = reformat_html_tags(content)
        print(f"[TIMER] reformat_html_tags: {time.perf_counter() - t4:.3f}s")

        text_list = [
            (page_contents.title, "title"),
            (page_contents.headings[0], "h1"),
            (page_contents.headings[1], "h2"),
            (page_contents.headings[2], "h3"),
            (page_contents.headings[3], "h4"),
            (page_contents.headings[4], "h5"),
            (page_contents.headings[5], "h6"),
            (page_contents.paragraphs, "p"),
            (page_contents.description, "description")
        ]

        keyword_pairs = defaultdict(float)
        t5 = time.perf_counter()
        clean_content = html_to_clean(content)
        print(f"[TIMER] html_to_clean: {time.perf_counter() - t5:.3f}s")

        clean_lower = clean_content.lower()
        word_freq = Counter(clean_lower.split())

        t6 = time.perf_counter()
        for text_items, element_type in text_list:
            importance = self.assign_importance_by_location(element_type)
            for text in text_items:
                words = extract_words(text)
                for word in words:
                    tf = 1 + log1p(word_freq.get(word.lower(), 0))
                    tf = 1 + log1p(tf)
                    tf_capped = min(tf, 3)
                    keyword_pairs[word] += importance * tf_capped
        print(f"[TIMER] keyword_pairs building: {time.perf_counter() - t6:.3f}s")

        words = clean_content.split()
        url_emb_pairs = set()
        t7 = time.perf_counter()
        for i in range(0, len(words), 400):
            chunk = ' '.join(words[i:i + 400])
            chunk_id = hash((url, i)) % (10 ** 9)
            self.vdb.insert(text=chunk, id=chunk_id)
            url_emb_pairs.add((chunk_id, url))
        print(f"[TIMER] vdb chunk insert ({len(url_emb_pairs)} chunks): {time.perf_counter() - t7:.3f}s")

        t8 = time.perf_counter()
        self.db.manage_vector_for_index_batch(list(url_emb_pairs))
        print(f"[TIMER] manage_vector_for_index_batch: {time.perf_counter() - t8:.3f}s")

        t9 = time.perf_counter()
        self.db.manage_for_index(url=url, pairs=keyword_pairs)
        print(f"[TIMER] manage_for_index: {time.perf_counter() - t9:.3f}s")

        print(f"[TIMER] TOTAL process: {time.perf_counter() - t0:.3f}s")