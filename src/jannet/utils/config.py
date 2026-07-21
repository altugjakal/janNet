class Config:

    MODEL = 'sentence-transformers/msmarco-distilbert-dot-v5'
    MODEL_OUTPUT_DIM = 768
    VECTOR_WEIGHT = 0.4
    LEXICAL_WEIGHT = 0.6

    USER_AGENT = "Jannetbot"

    EDU_TLDS = [".edu"]
    AUTHORITIVE_TLDS = [".com", ".net", ".org"]
    AUTHORITIVE_MULT = 1.0
    GENERIC_MULT = 0.7
    EDU_MULT = 2.0
    MAX_CRAWLS = 2200
    MAX_PROCESS = 2000

    RETURN_LIMIT = 10
    SCORE_FILTER = 0.000

    CORNET_URL = 'http://localhost:7777/'

    FIRST_POOL_SIZE = 5

    DB_PASSWORD = 'altug1601'
    DB_USER = 'altug'
    DB_DATABASE = 'defaultdb'
    DB_PORT = 3306
    DB_HOST = 'localhost'

    HTML_IMPORTANCE_MAP = {
        "title": 10,
        "h1": 9,
        "h2": 8,
        "h3": 7,
        "h4": 6,
        "h5": 5,
        "h6": 4,
        "p": 3,
        "description": 9,
        "domain": 3,
        "subdomain": 2,
        "path": 2,
        "param": 3
    }

    HTML_DEFAULT_WEIGHT = 1

    LEXICAL_POOL_SIZE = 30
    SEMANTIC_POOL_SIZE = 30

    PAGERANK_CALCULATION= False

    HF_TOKEN = "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"

    SLEEP_M = 0
    SLEEP_P = 0

    SEED_URLS = [
        ["https://en.wikipedia.org/wiki/Computer_science"],
    ]

    CRAWL_THREAD_COUNT = 1
    PROCESS_THREAD_COUNT = 1
    assert len(SEED_URLS) == CRAWL_THREAD_COUNT

    DESIGN_FILE_EXTS = (".png", ".jpg", ".jpeg", ".ico", ".webp", ".svg", ".css", ".docx")