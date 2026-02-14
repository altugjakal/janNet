import urllib
from collections import defaultdict
from math import log1p
from statistics import fmean
from urllib.parse import urlparse

import tldextract

from utils.config import Config
from utils.misc import make_request
from utils.misc import extract_words
from utils.parsing import reformat_html_tags, html_to_clean, get_domain, get_tld


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

    def search(self, term):

        terms = extract_words(term)

        url_temp_scores = defaultdict(int)

        total_url_count = self.db.get_total_url_count()

        contents = {}
        kw_counts = {}

        locations = self.db.search_index(terms, limit=Config.LEXICAL_POOL_SIZE)
        for term in terms:
            kw_counts[term] = self.db.get_total_kw_count(term.lower())

        for url, keyword, content, score in locations:
            if url not in contents:
                contents[url] = content
                for search_term in terms:
                    importance = self.assign_importance_by_frequency(html_to_clean(content), search_term, total_url_count, score)
                    url_temp_scores[url] += importance

        return url_temp_scores, contents
