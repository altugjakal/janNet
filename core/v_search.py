
from utils.misc import vectorise_text
from utils.data_handling import *
from core.vectordb.vectordb import VectorDB

def vector_search(term):
    db = VectorDB()
    term_vector = db.text_vectoriser(term)
    vectors = db.cosine_similarity(term_vector)

    results = []

    for id, score in vectors:
        if id == None:
            continue
        url = get_url_by_vector_id(id)


        results.append(url)

        if len(results) >= 20:  # limit
            break

    return results



