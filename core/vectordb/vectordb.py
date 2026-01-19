from core.model_manager import get_model
import numpy as np
import faiss

class VectorDB:
    def __init__(self, dimension=384):

        self.base_index = faiss.IndexFlatL2(dimension)
        self.index = faiss.IndexIDMap2(self.base_index)
    
#possible problem here -nvm
    def insert(self, vector, id):

        vector = np.array([vector]).astype('float32')
        id = np.array([id], dtype='int64')
        try:

            self.index.add_with_ids(vector, id)
        except Exception as e:
            print(e)


    def delete(self, id):
        id_to_remove = np.array([id], dtype='int64')
        self.index.remove_ids(id_to_remove)

    def find(self, id):
        self.index.reconstruct(id)

    def euclidian_d(self, query_vector, k=10):
        faiss.omp_set_num_threads(1)
        query = np.array([query_vector]).astype('float32')
        distances, ids = self.index.search(query, k)

#returns empty array - ids always -1


        return [
            {"id": int(id), "score": float(score)}
            for id, score in zip(ids[0], distances[0])
            if id != -1
        ]

    def vectorise_text(self, text):
        model = get_model()
        return model.encode(text)
