import random
import time

from protego import Protego

from src.jannet.utils.config import Config
from src.jannet.managers.db_manager import get_db, get_vdb
from src.jannet.utils.parsing import extract_anchors, html_to_clean, get_url_root, reformat_html_tags
from src.jannet.utils.misc import extract_words, make_request
from urllib.parse import urljoin

from src.jannet.utils.timer_wrapper import timed

@timed
class Crawl:
    def __init__(self, sleep_median, sleep_padding, db=get_db(), vdb=get_vdb(), thread_id=None):
        self.sleep_median = sleep_median
        self.sleep_padding = sleep_padding
        self.db = db
        self.vdb = vdb
        self.thread_id = thread_id

    def crawl(self, url, id):
        sleep_median = self.sleep_median
        sleep_padding = self.sleep_padding

        delay = None  # ← default so it's always defined

        try:
            r_url = get_url_root(url) + "/robots.txt"
            response = make_request(r_url)
            rp = Protego.parse(response.text)
            if not rp.can_fetch(Config.USER_AGENT, url):
                self.db.drop_from_queue(url, thread_id=self.thread_id)
                print(f"[Thread {self.thread_id}] Blocked by robots.txt: {url}")
                return
            delay = rp.crawl_delay(Config.USER_AGENT)
            print(f"[Thread {self.thread_id}] robots.txt OK for {url} (crawl-delay: {delay})")
        except Exception as e:
            print(f"[Thread {self.thread_id}] robots.txt fetch failed for {url}: {e}")

        try:
            content = make_request(url).text
            print(f"[Thread {self.thread_id}] 200 OK: {url}")
        except Exception as e:
            print(f"[Thread {self.thread_id}] Crawl failed for {url}: {e}")
            self.db.drop_from_queue(url, thread_id=self.thread_id)
            return

        self.db.drop_from_queue(url, thread_id=self.thread_id)
        if not content:
            print(f"[Thread {self.thread_id}] Empty content, skipping: {url}")
            return

        self.db.add_url(id, url, content)
        print(f"[Thread {self.thread_id}] Stored: {url}")

        sleep_time = delay if delay else (sleep_median + random.uniform(-sleep_padding, sleep_padding))
        print(f"[Thread {self.thread_id}] Sleeping {sleep_time:.2f}s")
        time.sleep(sleep_time)