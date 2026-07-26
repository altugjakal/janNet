import time


class SemanticSearch:
    def __init__(self, db=None, vdb=None):
        self.db = db
        self.vdb = vdb

    def search(self, term):
        t0 = time.perf_counter()

        t1 = time.perf_counter()
        term_vector = self.vdb.vectorise_text(term)
        vectors = self.vdb.euclidian_d(term_vector)
        print(f"[TIMER] vdb search: {time.perf_counter() - t1:.3f}s")

        t2 = time.perf_counter()

        id_scores = {}
        vector_ids = tuple([v['id'] for v in vectors])
        emb_ids, ids = self.db.get_id_by_vector_id_batch(vector_ids)
        print(f"[TIMER] db get_url_by_vector_id_batch: {time.perf_counter() - t2:.3f}s")

        t3 = time.perf_counter()
        score_by_vector_id = {
            vector["id"]: vector["score"]
            for vector in vectors
        }

        for emb_id, id, content in zip(emb_ids, ids):
            id_scores[id] += score_by_vector_id[emb_id]
        print(f"[TIMER] map results: {time.perf_counter() - t3:.3f}s")

        print(f"[TIMER] TOTAL search: {time.perf_counter() - t0:.3f}s")

        print({f"{id}: {score}" for id, score in id_scores.items()})

        return id_scores
