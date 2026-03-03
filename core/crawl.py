import random
import time
from collections import defaultdict, Counter
from math import log1p

from protego import Protego

from utils.config import Config
from managers.db_manager import get_db, get_vdb
from utils.parsing import extract_anchors, html_to_clean, get_url_root, reformat_html_tags
from utils.misc import extract_words, make_request
from urllib.parse import urljoin

from utils.timer_wrapper import timed


class Crawl:
    def __init__(self, sleep_median, sleep_padding, db=get_db(), vdb=get_vdb(), thread_id=None):

        self.sleep_median = sleep_median
        self.sleep_padding = sleep_padding
        self.db = db
        self.vdb = vdb
        self.thread_id = thread_id

    def assign_importance_by_location(self, element_type):
        base_importance = Config.HTML_IMPORTANCE_MAP.get(element_type, 1)
        return base_importance

    @timed
    def crawl(self, url):

        sleep_median = self.sleep_median
        sleep_padding = self.sleep_padding

        t0 = time.perf_counter()

        try:
            r_url = get_url_root(url) + "/robots.txt"
            response = make_request(r_url)
            rp = Protego.parse(response.text)
            if not rp.can_fetch(Config.USER_AGENT, url):
                self.db.drop_from_queue(url, thread_id=self.thread_id)
                print(f"Not allowed to crawl {url}")
                return
        except Exception as e:
            print(f"Could not fetch robots.txt for: {url} {e}")
        print(f"[TIMER] robots.txt fetch+parse: {time.perf_counter() - t0:.3f}s");
        t1 = time.perf_counter()

        try:
            content = make_request(url).text
            print(f"200: {url}")
        except Exception as e:
            print("Crawling failed for: ", url, e)
            self.db.drop_from_queue(url, thread_id=self.thread_id)
            return
        print(f"[TIMER] page fetch: {time.perf_counter() - t1:.3f}s");
        t2 = time.perf_counter()

        anchors, anchor_values = extract_anchors(content)

        to_be_queued = set()
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

            to_be_queued.add(absolute_url)
            new_count += 1
        print(f"[TIMER] anchor extraction + tuple building: {time.perf_counter() - t2:.3f}s");
        t3 = time.perf_counter()

        self.db.manage_for_index_batch(tuples)
        print(f"[TIMER] manage_for_index_batch: {time.perf_counter() - t3:.3f}s");
        t4 = time.perf_counter()

        self.db.add_to_queue_batch(list(to_be_queued), thread_id=self.thread_id)
        print(f"[TIMER] add_to_queue_batch ({new_count} urls): {time.perf_counter() - t4:.3f}s");
        t5 = time.perf_counter()

        if new_count > 0:
            print(f"  → Queued {new_count} new URLs")

        self.db.drop_from_queue(url, thread_id=self.thread_id)
        self.db.add_url(url, content)
        print(f"[TIMER] drop_from_queue + add_url: {time.perf_counter() - t5:.3f}s");
        t6 = time.perf_counter()

        page_contents = reformat_html_tags(content)
        print(f"[TIMER] reformat_html_tags: {time.perf_counter() - t6:.3f}s");
        t7 = time.perf_counter()

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
        clean_content = html_to_clean(content)
        print(f"[TIMER] html_to_clean: {time.perf_counter() - t7:.3f}s");
        t8 = time.perf_counter()

        clean_lower = clean_content.lower()
        word_freq = Counter(clean_lower.split())

        for text_items, element_type in text_list:
            importance = self.assign_importance_by_location(element_type)
            for text in text_items:
                words = extract_words(text)
                for word in words:
                    tf = 1 + log1p(word_freq.get(word.lower(), 0))
                    tf = 1 + log1p(tf)
                    tf_capped = min(tf, 3)
                    keyword_pairs[word] += importance * tf_capped
        print(f"[TIMER] keyword_pairs building: {time.perf_counter() - t8:.3f}s");
        t9 = time.perf_counter()

        words = clean_content.split()
        url_emb_pairs = set()
        for i in range(0, len(words), 400):
            chunk = ' '.join(words[i:i + 400])
            chunk_id = hash((url, i)) % (10 ** 9)
            self.vdb.insert(text=chunk, id=chunk_id)
            url_emb_pairs.add((chunk_id, url))
        print(f"[TIMER] vdb chunk insert ({len(url_emb_pairs)} chunks): {time.perf_counter() - t9:.3f}s");
        t10 = time.perf_counter()

        self.db.manage_vector_for_index_batch(list(url_emb_pairs))
        print(f"[TIMER] manage_vector_for_index_batch: {time.perf_counter() - t10:.3f}s");
        t11 = time.perf_counter()

        self.db.manage_for_index(url=url, pairs=keyword_pairs)
        print(f"[TIMER] manage_for_index: {time.perf_counter() - t11:.3f}s")

        print(f"[TIMER] TOTAL crawl (excl. sleep): {time.perf_counter() - t0:.3f}s")

        time.sleep(sleep_median + random.uniform(-sleep_padding, sleep_padding))