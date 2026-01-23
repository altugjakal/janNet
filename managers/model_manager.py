from sentence_transformers import SentenceTransformer
from utils.config import Config
_model = None

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(Config.MODEL)
        return _model
    else:
        return _model