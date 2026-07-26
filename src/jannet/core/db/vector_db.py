import os

import torch

from src.jannet.managers.model_manager import get_model
import numpy as np
import faiss
from src.jannet.utils.thread_lock_wrapper import db_locked, vdb_locked
from src.jannet.utils.config import Config

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

    @vdb_locked
    def insert(self, text: str, id: int) -> bool:
        vector = self.vectorise_text(text)

        vector = np.array([vector]).astype('float32')
        id = np.array([id], dtype='int64')
        try:

            self.index.add_with_ids(vector, id)
            return True

        except Exception as e:
            print(e)
            return False

    @vdb_locked
    def delete(self, id: int) -> bool:
        id_to_remove = np.array([id], dtype='int64')
        try:
            self.index.remove_ids(id_to_remove)
            return True

        except Exception as e:
            print(e)
            return False



    @db_locked
    def euclidian_d(self, query_vector: list[float] | np.ndarray, k=Config.SEMANTIC_POOL_SIZE) -> list[dict[str, int | float]]:
        faiss.omp_set_num_threads(1)
        query = np.array([query_vector]).astype('float32')
        distances, ids = self.index.search(query, k)


        return [
            {"id": int(id), "score": float(score)}
            for id, score in zip(ids[0], distances[0])
            if id != -1
        ]


    def vectorise_text(self, text: str) -> np.ndarray:
        model = get_model()
        vector = model.encode(text)
        return vector / np.linalg.norm(vector)


    def tokenize_text(self, text: str) -> np.ndarray:
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

    def save_to_disk(self) -> bool:
        current_dir = os.path.dirname(os.path.abspath(__file__))

        index_path = os.path.normpath(os.path.join(current_dir, "..", "..", "index", "index.index"))

        try:
            faiss.write_index(self.index, index_path)
            return True
        except (FileNotFoundError, RuntimeError):
            return False


