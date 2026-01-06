
from utils.misc import vectorise_text, rank
from utils.data_handling import *
from core.vectordb.vectordb import VectorDB

def vector_search(term):
    db = VectorDB()
    term_vector = db.text_vectoriser(term)
    vectors = db.cosine_similarity(term_vector)

    url_scores = {}
    results = []

    for id, score in vectors:


        url = get_url_by_vector_id(id)

        score = rank(url, score)


        url_scores[url] = score


    

    return url_scores


