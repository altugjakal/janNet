from collections import defaultdict
from math import log1p
from statistics import fmean
from urllib.parse import urlparse

import tldextract

from utils.config import Config
from utils.misc import make_request
from utils.misc import extract_keywords
from core.subscore import SubScore
from utils.regex import reformat_html_tags


class Search:
    def __init__(self, db):
        self.db = db

    def assign_importance(self, content, keyword, element_type):
        tf = content.lower().count(keyword.lower())
        tf = 1 + log1p(tf)
        tf_capped = min(tf, 3)
        idf = log1p(self.db.get_total_url_count() / max(1, self.db.get_total_kw_count(keyword.lower())))
        tfidf = tf_capped * idf
        phrase_bonus = len(keyword.split()) * 0.5
        base_importance = Config.HTML_IMPORTANCE_MAP.get(element_type, 1) * tfidf * (1 + phrase_bonus)
        return base_importance

    def search(self, term):
        terms = extract_keywords(term)

        url_temp_scores = defaultdict(list)
        url_scores = defaultdict(int)


        contents = {}

        locations = self.db.search_index(terms)

        for url, keyword in locations:


            content = make_request(url).text
            contents[url] = content
            content, texts = reformat_html_tags(content)


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
                            importance = self.assign_importance(text, search_term, element_type)
                            url_temp_scores[url].append(importance)

            for url, importances in url_temp_scores.items():
                url_scores[url] = SubScore.get_url_rank(url, fmean(importances))


        return url_scores, contents
