from utils.parsing import html_to_clean
from utils.timer_wrapper import timed


class SemanticSearch():
    def __init__(self, db=None, vdb=None):
        self.db = db
        self.vdb = vdb

    @timed
    def search(self, term):

        term_vector = self.vdb.vectorise_text(term)
        vectors = self.vdb.euclidian_d(term_vector)

        map_s = {}

        url_scores = {}
        url_contents = {}
        vector_ids = [v['id'] for v in vectors]
        ids, urls, contents = self.db.get_url_by_vector_id_batch(vector_ids)

        for vector in vectors:
            map_s[vector['id']] = vector['score']

        for id, url, content in zip(ids, urls, contents):

            url_scores[url] = map_s[id]
            url_contents[url] = content

        return url_scores, url_contents


