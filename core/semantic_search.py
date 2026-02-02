


class SemanticSearch():
    def __init__(self, db=None, vdb=None):
        self.db = db
        self.vdb = vdb

    def search(self, term):

        term_vector = self.vdb.vectorise_text(term)
        vectors = self.vdb.euclidian_d(term_vector)


        url_scores = {}
        url_contents = {}

        for vector in vectors:

            url, content = self.db.get_url_by_vector_id(vector['id'])

            url_scores[url] = vector['score']
            url_contents[url] = content


        return url_scores, url_contents


