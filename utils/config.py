from dataclasses import dataclass

@dataclass
class Config:
    MODEL = 'all-mpnet-base-v2'
    MODEL_OUTPUT_DIM = 768
    VECTOR_WEIGHT = 0.4
    LEXICAL_WEIGHT = 0.6

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
        "https://en.wikipedia.org/wiki/Albert_Einstein",
        "https://en.wikipedia.org/wiki/Python_(programming_language)",
        "https://en.wikipedia.org/wiki/Black_hole",
        "https://en.wikipedia.org/wiki/Tokyo",
        "https://en.wikipedia.org/wiki/The_Beatles",
    ]
