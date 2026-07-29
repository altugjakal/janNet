
from src.jannet.utils.config import Config
_model = None

def get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(Config.MODEL, trust_remote_code=True)
        return _model
    else:
        return _model

