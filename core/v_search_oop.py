from utils.misc import vectorise_text, rank, make_request
from utils.data_handling import *
from core.vectordb.vectordb import VectorDB

class VectorSearch():
    def __init__(self, db):
        self.db  = db

    def search(self, term):
        db = VectorDB()
        term_vector = db.text_vectoriser(term)
        vectors = db.cosine_similarity(term_vector)

        url_scores = {}
        url_contents = {}
        results = []

        for id, score in vectors:
            url = get_url_by_vector_id(id)

            try:
                url_contents[url] = make_request(url).text
            except:
                print("Failed request for content on: Vector Search, For: ", url)
                continue


            score = rank(url, score)
            url_scores[url] = score


        return url_scores, url_contents


