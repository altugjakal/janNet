import math
from collections import defaultdict
from time import time
from math import log1p

from src.jannet.core.process.reverse_index import ReverseIndexCommunicator
from src.jannet.utils.config import Config
from src.jannet.utils.misc import extract_words
from src.jannet.utils.timer_wrapper import timed


class LexicalSearch:
    def __init__(self, db):
        self.db = db
        self.ri_client = ReverseIndexCommunicator()

    #optimize tomorrow, plus maybe have lexical pool size included
    @timed
    def search(self, term):

        def dot_product(a, b):
            return sum(x * y for x, y in zip(a, b))

        def cosine_similarity(a, a_length, b, b_length):
            top = dot_product(a, b)
            bottom = a_length * b_length
            return top / bottom

        terms = extract_words(term)

        results = self.ri_client.search(terms)
        total_url_count = self.db.get_total_url_count()

        print(results)

        doc_ids = [
            item["docId"]
            for result in results
            for item in result["postingItems"]
        ]
        contents = self.db.get_contents_by_ids(doc_ids)

        id_scores = {}

        vectors = defaultdict(lambda: [0.0] * len(set(terms)))
        term_vector = [0.0] * len(set(terms))

        for i, result in enumerate(results):
            df = len(result["postingItems"])
            idf = log1p((total_url_count + 1) / (df + 1)) + 1

            term_tf = terms.count(result["token"]) / len(terms)
            term_tfidf = term_tf * idf
            term_vector[i] = term_tfidf

            for posting in result["postingItems"]:
                doc_length = len(contents[posting["docId"]].split())

                #here, account for hit weights
                tf = len(posting["hits"]) / doc_length
                tfidf = tf * idf

                vectors[posting["docId"]][i] = tfidf

        query_length = math.sqrt(len(terms))

        for doc_id, doc_vector in vectors.items():
            content = contents.get(doc_id)
            if not content:
                continue

            doc_length_raw = len(content.split())

            if doc_length_raw > 0 and query_length > 0:

                doc_length_norm = math.sqrt(doc_length_raw)

                score = cosine_similarity(term_vector, query_length, doc_vector, doc_length_norm)
                if score > 0:
                    id_scores[doc_id] = score

                    #return url score mappings not id score, the other end expects URLs for final result display

        map_over_ids = self.db.get_url_from_ids(id_scores.keys())

        url_scores = {url: id_scores[id] for id, url in map_over_ids if id in id_scores}

        return url_scores, contents
