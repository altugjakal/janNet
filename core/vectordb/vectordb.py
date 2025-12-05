from utils.data_handling import *
from utils.misc import vectorise_text
import numpy as np


class VectorDB:
    def __init__(self):
        pass
    

    def insert(self, vector, id=None):
        
        if id is None:
            id = np.random.randint(0, 10000)
        return add_vector(vector, id)

    def delete(self, id):
        return delete_vector(id)

    def find(self, id):
        return get_vector(id)

    def cosine_similarity(self, input_vector):
        return cosine_similarity_vectors(input_vector)

    def text_vectoriser(self, text):
        return vectorise_text(text)
