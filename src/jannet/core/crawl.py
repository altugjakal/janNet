import logging
import random
import time

from protego import Protego

from src.jannet.utils.config import Config
from src.jannet.managers.db_manager import get_db, get_vdb
from src.jannet.utils.parsing import get_url_root, get_domain
from src.jannet.utils.misc import  make_getr


logger = logging.getLogger(__name__)

class Crawl:
    def __init__(self, sleep_median, sleep_padding, db=get_db(), vdb=get_vdb(), rc=None, thread_id=None):
        self.sleep_median = sleep_median
        self.sleep_padding = sleep_padding
        self.db = db
        self.vdb = vdb
        self.thread_id = thread_id
        self.rc = rc

    def crawl(self, url, id):
        sleep_median = self.sleep_median
        sleep_padding = self.sleep_padding

        domain = get_domain(url)

        if self.db.is_url_visited(url):
            logger.info("Thread %d: %s already visited", self.thread_id, url)
            self.db.drop_from_queue(url, thread_id=self.thread_id)
            return


        try:
            is_allowed, delay = self.rc.check(domain, url)
            if not is_allowed:
                return
        except KeyError:
            delay = None
            disallowed_pages = []
            try:

                r_url = get_url_root(url) + "/robots.txt"
                response = make_getr(r_url)
                rp = Protego.parse(response.text)
                can_fetch = rp.can_fetch(Config.USER_AGENT, url)
                delay = rp.crawl_delay(Config.USER_AGENT)
                disallowed_pages =[]
                for rule in rp.robot_rules[Config.USER_AGENT]:
                    if rule['type'] == 'disallow':
                        disallowed_pages.append(rule['path'])


                if not can_fetch:
                    self.db.drop_from_queue(url, thread_id=self.thread_id)
                    logger.warning("Thread %d: blocked by robots.txt: %s", self.thread_id, url)
                    return

                logger.info("Thread %d: robots.txt OK for: %s", self.thread_id, url)
            except Exception as e:

                logger.exception("Thread %d: robots.txt fetch failed for %s", self.thread_id, url)

            self.rc.add(domain, disallowed_pages, delay)



        try:
            content = make_getr(url).text
            logger.info(f"Thread %d: 200 OK for %s" , self.thread_id, url)
        except Exception as e:
            logger.exception("Thread %d: crawl failed for %s", self.thread_id, url)
            self.db.drop_from_queue(url, thread_id=self.thread_id)
            return

        self.db.drop_from_queue(url, thread_id=self.thread_id)
        if not content:
            logger.warning("Thread %d: Empty content", self.thread_id)
            return

        self.db.add_url(id, url, content)
        logger.info("Thread %d: stored %s", self.thread_id, url)


        sleep_time = delay if delay else (sleep_median + random.uniform(-sleep_padding, sleep_padding))
        logger.info("Thread %d: sleeping %.2fs", self.thread_id, sleep_time)
        time.sleep(sleep_time)