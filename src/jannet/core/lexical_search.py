from collections import defaultdict
from time import time
from math import log1p

from src.jannet.utils.config import Config
from src.jannet.utils.misc import extract_words
from src.jannet.utils.timer_wrapper import timed


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
        t0 = time()

        terms = extract_words(term)
        print(f"[lexical] extract_words:           {(time()-t0)*1000:.1f}ms | terms={terms}")

        t1 = time()
        url_temp_scores = defaultdict(int)
        total_url_count = self.db.get_total_url_count()
        print(f"[lexical] get_total_url_count:     {(time()-t1)*1000:.1f}ms | count={total_url_count}")

        contents = {}

        t2 = time()
        locations = self.db.search_index(terms, limit=Config.LEXICAL_POOL_SIZE)
        print(f"[lexical] search_index:            {(time()-t2)*1000:.1f}ms | results={len(locations)}")

        t3 = time()
        kw_counts = self.db.get_total_kw_count_batch(terms)
        print(f"[lexical] get_total_kw_count_batch:{(time()-t3)*1000:.1f}ms | kw_counts={kw_counts}")

        t4 = time()
        for url, keyword, content, score in locations:
            if content:
                contents[url] = content
                for search_term in terms:
                    importance = self.assign_importance_by_idf(keyword, total_url_count, kw_counts[search_term])
                    url_temp_scores[url] += importance * score
        print(f"[lexical] scoring loop:            {(time()-t4)*1000:.1f}ms | urls_scored={len(url_temp_scores)}")

        print(f"[lexical] TOTAL search():          {(time()-t0)*1000:.1f}ms")

        return url_temp_scores, contents