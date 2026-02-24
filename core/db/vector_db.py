import torch

from managers.model_manager import get_model
import numpy as np
import faiss
from utils.thread_lock_wrapper import locked
from utils.config import Config

class VectorDB:
    def __init__(self, dimension=Config.MODEL_OUTPUT_DIM):

        if torch.cuda.is_available():
            self.device = torch.device("cuda")
        elif torch.backends.mps.is_available():
            self.device = torch.device("mps")
        else:
            self.device = torch.device("cpu")

        try:
            self.index = faiss.read_index("index/index.index")
        except (FileNotFoundError, RuntimeError):
            self.base_index = faiss.IndexFlatL2(dimension)
            self.index = faiss.IndexIDMap2(self.base_index)

# gotta handle multiple passages here, id is not the unique identifier here
    @locked
    def insert(self, text, id):
        vector = self.vectorise_text(text)

        vector = np.array([vector]).astype('float32')
        id = np.array([id], dtype='int64')
        try:

            self.index.add_with_ids(vector, id)

        except Exception as e:
            print(e)

    @locked
    def delete(self, id):
        id_to_remove = np.array([id], dtype='int64')
        self.index.remove_ids(id_to_remove)

    @locked
    def find(self, id):
        self.index.reconstruct(id)

    @locked
    def euclidian_d(self, query_vector, k=Config.SEMANTIC_POOL_SIZE):
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
        ).to(self.device)

        with torch.no_grad():
            output = model[0].auto_model(**encoded)

        token_embeddings = output.last_hidden_state
        attention_mask = encoded['attention_mask']

        return token_embeddings

    def save_to_disk(self):
        faiss.write_index(self.index, "index/index.index")
