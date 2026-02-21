import random
import time
import traceback
import urllib
from collections import defaultdict
from math import log1p

from protego import Protego

from utils.config import Config
from managers.db_manager import get_db, get_vdb
from utils.parsing import extract_anchors, html_to_clean, get_url_root, reformat_html_tags
from utils.misc import extract_words, make_request
from urllib.parse import urljoin


class Crawl():
    def __init__(self, sleep_median, sleep_padding, db=get_db(), vdb=get_vdb(), thread_id=None):

        self.sleep_median = sleep_median
        self.sleep_padding = sleep_padding
        self.db = db
        self.vdb = vdb
        self.thread_id = thread_id

    def assign_importance_by_location(self, element_type):
        base_importance = Config.HTML_IMPORTANCE_MAP.get(element_type, 1)
        return base_importance

    def crawl(self, url):

        sleep_median = self.sleep_median
        sleep_padding = self.sleep_padding

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

        try:
            content = make_request(url).text
            print(f"200: {url}")
        except Exception as e:
            print("Crawling failed for: ", url, e)
            self.db.drop_from_queue(url, thread_id=self.thread_id)
            return

        anchors, anchor_values = extract_anchors(content)

        # Discover and queue new URLs - huge bottleneck, use sets and batch insertion

        to_be_queued = set()
        new_count = 0
        tuples = []
        for anchor, a_v in zip(anchors, anchor_values):
            absolute_url = urljoin(url, anchor)
            absolute_url = absolute_url.rstrip("/")
            absolute_url = absolute_url.split("#")[0]


            for value in extract_words(a_v):
                tuples.append((absolute_url, value, Config.HTML_IMPORTANCE_MAP.get("p")))


            #add items to index from anchor text value

            if not absolute_url.startswith(("http://", "https://")):
                continue

            if absolute_url.endswith(Config.DESIGN_FILE_EXTS):
                continue

            to_be_queued.add(absolute_url)
            new_count += 1

        self.db.manage_for_index_batch(tuples)
        self.db.add_to_queue_batch(list(to_be_queued), thread_id=self.thread_id)


        if new_count > 0:
            print(f"  → Queued {new_count} new URLs")

        self.db.drop_from_queue(url, thread_id=self.thread_id)
        self.db.add_url(url, content)

        page_contents = reformat_html_tags(content)

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

        for text_items, element_type in text_list:
            importance = self.assign_importance_by_location(element_type)

            for text in text_items:
                words = extract_words(text)  # Get list of words
                for word in words:
                    tf = clean_content.lower().count(word.lower())
                    tf = 1 + log1p(tf)
                    tf_capped = min(tf, 3)
                    keyword_pairs[word] += importance * tf_capped

        # add overlap logic + passage ranking

        words = clean_content.split()
        for i in range(0, len(words), 400):
            chunk = ' '.join(words[i:i + 400])
            chunk_id = hash((url, i)) % (10 ** 9)
            self.vdb.insert(text=chunk, id=chunk_id)
            self.db.manage_vector_for_index(url=url, emb_id=chunk_id)

        self.db.manage_for_index(url=url, pairs=keyword_pairs)

        time.sleep(sleep_median + random.uniform(-sleep_padding, sleep_padding))
