import logging
import math
from collections import defaultdict
from time import time
from math import log1p

from src.jannet.core.process.reverse_index import ReverseIndexCommunicator
from src.jannet.utils.config import Config
from src.jannet.utils.misc import extract_words
from src.jannet.utils.timer_wrapper import timed

logger = logging.getLogger(__name__)


class LexicalSearch:
    def __init__(self, db, b=0.75, k=1.2):
        self.db = db
        self.ri_client = ReverseIndexCommunicator()
        self.b = b
        self.k = k
        self.avg_doc_length = 2200

    def bm25(self, tf, doc_length, idf):
        bm25 = (((self.k + 1) * tf) / (self.k * ((1 - self.b) + self.b * (doc_length / self.avg_doc_length)) + tf)) * idf
        return bm25

    # optimize tomorrow, plus maybe have lexical pool size included
    @timed
    def search(self, term):

        terms = extract_words(term)

        t1 = time()
        results = self.ri_client.search(terms)

        if not results:
            logger.info("Lexical search returned no results")
            return {}

        t2 = time()
        logger.info("ri_client.search completed in %.6fs", t2 - t1)

        total_url_count = self.db.get_total_url_count()

        doc_ids = [
            item["docId"]
            for result in results
            for item in result["postingItems"]
        ]

        t3 = time()
        content_lengths = self.db.get_content_lengths_by_ids(doc_ids)
        t4 = time()
        logger.info(
            "Fetched %d content lengths in %.6fs",
            len(content_lengths),
            t4 - t3
        )

        t5 = time()
        id_scores = {}

        vectors = defaultdict(lambda: [0.0] * len(terms))
        term_vector = [0.0] * len(terms)

        for i, result in enumerate(results):
            df = len(result["postingItems"])
            idf = log1p((total_url_count + 1) / (df + 1)) + 1

            query_length = len(terms)
            term_tf = terms.count(result["token"])
            term_bm25 = self.bm25(term_tf, query_length, idf)
            term_vector[i] = term_bm25

            for posting in result["postingItems"]:
                doc_length = content_lengths[posting["docId"]]

                if doc_length == 0:
                    continue

                tf = sum(hit["weight"] for hit in posting["hits"])
                bm25 = self.bm25(tf, doc_length, idf)

                vectors[posting["docId"]][i] = bm25

        for doc_id, doc_vector in vectors.items():

            score = sum(x * y for x, y in zip(term_vector, doc_vector))

            if score > 0:
                id_scores[doc_id] = score

        t6 = time()
        logger.info("BM25 scoring completed in %.6fs", t6 - t5)

        t7 = time()

        t8 = time()
        logger.info("URL mapping completed in %.6fs", t8 - t7)

        logger.debug("Lexical scores: %s", id_scores)

        return id_scores