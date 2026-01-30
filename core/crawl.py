import random
from math import log1p
import time
from utils.config import Config
from managers.db_manager import get_db, get_vdb
from utils.regex import extract_anchors, reformat_html_tags
from utils.misc import extract_keywords, make_request
import tldextract

from urllib.parse import urljoin, urlparse


class Crawl():
    def __init__(self, sleep_median, sleep_padding, db=get_db(), vdb=get_vdb()):

        self.sleep_median = sleep_median
        self.sleep_padding = sleep_padding
        self.db = db
        self.vdb = vdb

    def crawl(self, url):
        # Check if already visited

        sleep_median = self.sleep_median
        sleep_padding = self.sleep_padding

        if self.db.is_url_visited(url):
            self.db.drop_from_queue(url)
            return



        try:
            content = make_request(url).text
        except Exception as e:
            print("Crawling failed for: ", url)
            print(e)
            return



        anchors = extract_anchors(content)

        # Discover and queue new URLs
        new_count = 0
        for anchor in anchors:
            absolute_url = urljoin(url, anchor)

            if not absolute_url.startswith(("http://", "https://")):
                continue

            absolute_url = absolute_url.rstrip("/")
            absolute_url = absolute_url.split("#")[0]

            if not self.db.is_url_visited(absolute_url) and not self.db.is_in_queue(absolute_url):
                self.db.add_to_queue(absolute_url)
                new_count += 1



        if new_count > 0:
            print(f"  → Queued {new_count} new URLs")

        # Index content
        content, texts = reformat_html_tags(content)

        self.db.drop_from_queue(url)
        self.db.add_url(url, content)

        #add overlap logic
        words = content.split()
        for i in range(0, len(words), 400):
            chunk = ' '.join(words[i:i + 400])
            chunk_id = hash((url, i)) % (10 ** 9)
            self.vdb.insert(text=chunk, id=chunk_id)
            self.db.manage_vector_for_index(url=url, emb_id=chunk_id)

        self.db.manage_for_index(url=url, keywords=extract_keywords(content))

        print(f"200: {url}")
        time.sleep(sleep_median + random.uniform(-sleep_padding, sleep_padding))
