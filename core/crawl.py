import random
from math import log1p
import time
from constants import html_importance_map
from utils.regex import extract_anchors, get_domain, reformat_html_tags
from utils.misc import extract_keywords, make_request
import tldextract
from utils.data_handling import *
from urllib.parse import urljoin, urlparse

class Crawl():
    def __init__(self, sleep_median, sleep_padding, db):

        self.sleep_median = sleep_median
        self.sleep_padding = sleep_padding
        self.db = db

    def assign_importance(self, content, keyword, element_type):
        tf = content.lower().count(keyword.lower())
        tf = 1 + log1p(tf)
        tf_capped = min(tf, 3)
        idf = get_total_url_count()/ max(1, get_total_kw_count(keyword.lower()))
        tfidf = tf_capped * idf
        phrase_bonus = len(keyword.split()) * 0.5
        base_importance = html_importance_map.get(element_type, 1) * tfidf * (1 + phrase_bonus)
        return base_importance


    def crawl(self, url):
        # Check if already visited

        db = self.db
        sleep_median = self.sleep_median
        sleep_padding = self.sleep_padding

        if is_url_visited(url):
            drop_from_queue(url)
            return

        # Mark as crawled
        add_url(url)
        drop_from_queue(url)


        try:
            content = make_request(url).text
        except Exception as e:
            return

        anchors = extract_anchors(content)

        # Discover and queue new URLs
        new_count = 0
        for anchor in anchors:
            absolute_url = urljoin(url, anchor)

            if not absolute_url.startswith(("http://", "https://")):
                continue

            absolute_url = absolute_url.rstrip("/")
            absolute_url = absolute_url.rstrip("#")


            if not is_url_visited(absolute_url) and not is_in_queue(absolute_url):
                add_to_queue(absolute_url)
                new_count += 1

        if new_count > 0:
            print(f"  → Queued {new_count} new URLs")

        # Index content
        content, texts = reformat_html_tags(content)

        try:
            vector = db.vectorise_text(content)
            id = hash(url) % (10 ** 9)
            db.insert(vector=vector, id=id)
            manage_vector_for_index(url=url, emb_id=id)
        except Exception as e:
            print(f"Vector error: {e}")

        # Extract keywords
        url_obj = urlparse(url)
        domain = tldextract.extract(url).domain
        paths = [p for p in url_obj.path.split('/') if p]
        subdomains = url_obj.netloc.split('.')[:-2]
        params = [p for p in url_obj.query.split('&') if p] if url_obj.query else []

        text_list = [
            (texts[0] if len(texts) > 0 else [], "title"),
            (texts[1] if len(texts) > 1 else [], "h1"),
            (texts[2] if len(texts) > 2 else [], "h2"),
            (texts[3] if len(texts) > 3 else [], "h3"),
            (texts[4] if len(texts) > 4 else [], "h4"),
            (texts[5] if len(texts) > 5 else [], "h5"),
            (texts[6] if len(texts) > 6 else [], "h6"),
            (texts[7] if len(texts) > 7 else [], "p"),
            (texts[8] if len(texts) > 8 else [], "description"),
            ([domain] if domain else [], "domain"),
            (subdomains if subdomains else [], "subdomain"),
            (paths if paths else [], "path"),
            (params if params else [], "param")
        ]

        for text_items, element_type in text_list:
            keyword_scores = {}
            for text in text_items:
                for word in extract_keywords(text):
                    importance = self.assign_importance(text, word, element_type)
                    keyword_scores[word] = keyword_scores.get(word, 0) + importance

            if keyword_scores:
                manage_for_index(url=url, pairs=keyword_scores)

        print(f"200: {url}")
        time.sleep(sleep_median + random.uniform(-sleep_padding, sleep_padding))