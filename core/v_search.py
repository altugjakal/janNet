from utils.misc import rank, make_request
from utils.data_handling import *
from core.vectordb.vectordb import VectorDB

class VectorSearch():
    def __init__(self, db):
        self.db = db

    def search(self, term):

        term_vector = self.db.vectorise_text(term)
        vectors = self.db.euclidian_d(term_vector)


        url_scores = {}
        url_contents = {}
        results = []



        for vector in vectors:

            url = get_url_by_vector_id(vector['id'])

            try:
                url_contents[url] = make_request(url).text
            except:
                print("Failed request for content on: Vector Search, For: ", url)
                continue


            score = rank(url, vector['score'])
            url_scores[url] = vector['score']


        return url_scores, url_contents


