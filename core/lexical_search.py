import urllib
from collections import defaultdict
from math import log1p
from statistics import fmean
from urllib.parse import urlparse

import tldextract

from utils.config import Config
from utils.misc import make_request
from utils.misc import extract_words
from utils.regex import reformat_html_tags, html_to_clean, get_domain, get_tld


class LexicalSearch:
    def __init__(self, db):
        self.db = db

    def assign_importance_by_frequency(self, text, keyword, total_url_count, kw_count):
        tf = text.lower().count(keyword.lower())
        tf = 1 + log1p(tf)
        tf_capped = min(tf, 3)
        idf = log1p(total_url_count / max(1, kw_count))
        tfidf = tf_capped * idf
        phrase_bonus = len(keyword.split()) * 0.5
        base_importance = tfidf * (1 + phrase_bonus)
        return base_importance

    def assign_importance_by_location(self, element_type):
        base_importance = Config.HTML_IMPORTANCE_MAP.get(element_type, 1)
        return base_importance

    def search(self, term):
        terms = extract_words(term)

        url_temp_scores = defaultdict(int)

        total_url_count = self.db.get_total_url_count()

        contents = {}
        kw_counts = {}

        locations = self.db.search_index(terms)
        for term in terms:
            kw_counts[term] = self.db.get_total_kw_count(term.lower())



        for url, keyword, content in locations:

            contents[url] = content
            texts = reformat_html_tags(content)

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
                for text in text_items:
                    for search_term in terms:
                        if search_term.lower() in text.lower():
                            importance = self.assign_importance_by_frequency(text, search_term, total_url_count, kw_counts[search_term]) * self.assign_importance_by_location(
                                element_type)
                            url_temp_scores[url] += importance

        return url_temp_scores, contents
