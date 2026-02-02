import torch

from managers.model_manager import get_model
import numpy as np
import faiss
from utils.config import Config

class VectorDB:
    def __init__(self, dimension=Config.MODEL_OUTPUT_DIM):

        try:
            self.index = faiss.read_index("db/index.index")
        except (FileNotFoundError, RuntimeError):
            self.base_index = faiss.IndexFlatL2(dimension)
            self.index = faiss.IndexIDMap2(self.base_index)

# handle multiple passages here, id is not the unique identifier here
    def insert(self, text, id):

        vector = self.vectorise_text(text)

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
        vector = model.encode(text)
        return vector / np.linalg.norm(vector)

    def tokenize_text(self, text):
        model = get_model()
        encoded = model.tokenizer(
            text,
            padding=True,
            truncation=True,
            return_tensors='pt'
        ).to("mps")

        with torch.no_grad():
            output = model[0].auto_model(**encoded)

        token_embeddings = output.last_hidden_state
        attention_mask = encoded['attention_mask']

        return token_embeddings

    def save_to_disk(self):
        faiss.write_index(self.index, "db/index.index")

