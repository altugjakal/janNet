from core.subscore import SubScore
from utils.misc import make_request


class VectorSearch():
    def __init__(self, db=None, vdb=None):
        self.db = db
        self.vdb = vdb

    def search(self, term):

        term_vector = self.vdb.vectorise_text(term)
        vectors = self.vdb.euclidian_d(term_vector)


        url_scores = {}
        url_contents = {}
        results = []

        for vector in vectors:

            url = self.db.get_url_by_vector_id(vector['id'])

            try:
                url_contents[url] = make_request(url).text
            except:
                print("Failed request for content on: Vector Search, For: ", url)
                continue


            score = SubScore.get_url_rank(url, vector['score'])
            url_scores[url] = vector['score']


        return url_scores, url_contents


