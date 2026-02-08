import random
import time
import urllib

from utils.config import Config
from managers.db_manager import get_db, get_vdb
from utils.regex import extract_anchors, html_to_clean, get_url_root
from utils.misc import extract_words, make_request
import urllib.robotparser as urobot
from urllib.parse import urljoin


class Crawl():
    def __init__(self, sleep_median, sleep_padding, db=get_db(), vdb=get_vdb(), thread_id=None):

        self.sleep_median = sleep_median
        self.sleep_padding = sleep_padding
        self.db = db
        self.vdb = vdb
        self.thread_id = thread_id

    def crawl(self, url):

        sleep_median = self.sleep_median
        sleep_padding = self.sleep_padding

        rp = urobot.RobotFileParser()
        try:
            r_url = get_url_root(url) + "/robots.txt"
            rp.set_url(r_url)
            rp.read()
            if not rp.can_fetch(Config.USER_AGENT, r_url):
                self.db.drop_from_queue(url, thread_id=self.thread_id)
                return
        except Exception as e:
            print(f"Could not fetch robots.txt for: {r_url} {e}")


        try:
            content = make_request(url).text
        except Exception as e:
            print("Crawling failed for: ", url)
            self.db.drop_from_queue(url, thread_id=self.thread_id)
            return

        anchors = extract_anchors(content)

        # Discover and queue new URLs
        new_count = 0
        for anchor in anchors:
            absolute_url = urljoin(url, anchor)
            absolute_url = absolute_url.rstrip("/")
            absolute_url = absolute_url.split("#")[0]


            if self.db.is_url_visited(absolute_url):
                continue

            if not absolute_url.startswith(("http://", "https://")):
                continue

            if absolute_url.endswith(Config.DESIGN_FILE_EXTS):
                continue

            if not self.db.is_url_visited(absolute_url) and not self.db.is_in_queue(absolute_url, thread_id=self.thread_id):
                self.db.add_to_queue(absolute_url, thread_id=self.thread_id)
                new_count += 1



        if new_count > 0:
            print(f"  → Queued {new_count} new URLs")


        self.db.drop_from_queue(url, thread_id=self.thread_id)
        self.db.add_url(url, content)

        #add overlap logic
        clean_content = html_to_clean(content)
        words = clean_content.split()
        for i in range(0, len(words), 400):
            chunk = ' '.join(words[i:i + 400])
            chunk_id = hash((url, i)) % (10 ** 9)
            self.vdb.insert(text=chunk, id=chunk_id)
            self.db.manage_vector_for_index(url=url, emb_id=chunk_id)

        self.db.manage_for_index(url=url, keywords=extract_words(content))

        print(f"200: {url}")
        time.sleep(sleep_median + random.uniform(-sleep_padding, sleep_padding))
