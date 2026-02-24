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
    MAX_CRAWLS = 10000
    RETURN_LIMIT = 100
    SCORE_FILTER = 0.050

    FIRST_POOL_SIZE = 10

    DB_PASSWORD = 'AVNS_hZabM_xFW7WDqJyALT8'
    DB_USER = 'doadmin'
    DB_DATABASE = 'defaultdb'
    DB_PORT = 25060
    DB_HOST = 'db-mysql-fra1-39054-do-user-17164387-0.g.db.ondigitalocean.com'

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

    LEXICAL_POOL_SIZE = 30
    SEMANTIC_POOL_SIZE = 30

    SEED_URLS = [
        ["https://en.wikipedia.org/wiki/Information_retrieval"],
        ["https://en.wikipedia.org/wiki/Search_engine"],
        ["https://arxiv.org/list/cs.AI/recent"],
    ]

    THREAD_COUNT = 3
    assert len(SEED_URLS) == THREAD_COUNT

    DESIGN_FILE_EXTS = (".png", ".jpg", ".jpeg", ".ico", ".webp", ".svg", ".css", ".docx")
