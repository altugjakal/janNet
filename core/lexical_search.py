from collections import defaultdict
from math import log1p

from utils.config import Config
from utils.misc import extract_words
from utils.timer_wrapper import timed


class LexicalSearch:
    def __init__(self, db):
        self.db = db

    def assign_importance_by_idf(self, keyword, total_url_count, kw_count):
        idf = log1p(total_url_count / max(1, kw_count)) + 1
        phrase_bonus = len(keyword.split()) * 0.5
        base_importance = idf * (1 + phrase_bonus)
        return base_importance

    @timed
    def search(self, term):

        terms = extract_words(term)

        url_temp_scores = defaultdict(int)

        total_url_count = self.db.get_total_url_count()

        contents = {}

        locations = self.db.search_index(terms, limit=Config.LEXICAL_POOL_SIZE)
        #bneck
        kw_counts = self.db.get_total_kw_count_batch(terms)

        for url, keyword, content, score in locations:

            if url not in contents:
                if content:
                    contents[url] = content
                    for search_term in terms:
                        importance = self.assign_importance_by_idf(keyword, total_url_count, kw_counts[search_term])
                        url_temp_scores[url] += importance * score

        return url_temp_scores, contents
