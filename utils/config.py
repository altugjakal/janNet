from dataclasses import dataclass

@dataclass
class Config:
    MODEL = 'all-distilroberta-v1'
    MODEL_OUTPUT_DIM = 768
    VECTOR_WEIGHT = 0.3
    LEXICAL_WEIGHT = 0.7

    EDU_TLDS = [".edu"]
    AUTHORITIVE_TLDS = [".com", ".net", ".org"]
    AUTHORITIVE_MULT = 1.0
    GENERIC_MULT = 0.7
    EDU_MULT = 2.0
    MAX_CRAWLS = 10000
    SCORE_FILTER = 0.400

    HTML_IMPORTANCE_MAP = {
        "title": 10,
        "h1": 9,
        "h2": 8,
        "h3": 7,
        "h4": 6,
        "h5": 5,
        "h6": 4,
        "p": 2,
        "description": 9,
        "domain": 3,
        "subdomain": 2,
        "path": 2,
        "param": 3

    }

    SEED_URLS = [
        "https://www.imdb.com/title/tt0246578/"
    ]
