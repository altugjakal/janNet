import time


class SemanticSearch:
    def __init__(self, db=None, vdb=None):
        self.db = db
        self.vdb = vdb

    def search(self, term):

        term_vector = self.vdb.vectorise_text(term)
        vectors = self.vdb.euclidian_d(term_vector)



        id_scores = {}
        vector_ids = tuple([v['id'] for v in vectors])
        emb_ids, ids = self.db.get_id_by_vector_id_batch(vector_ids)


        score_by_vector_id = {
            vector["id"]: vector["score"]
            for vector in vectors
        }

        for emb_id, id, content in zip(emb_ids, ids):
            id_scores[id] += score_by_vector_id[emb_id]



        return id_scores
