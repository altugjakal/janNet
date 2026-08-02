import os
from dotenv import load_dotenv

class Config:
    load_dotenv()

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
    MAX_CRAWLS = 650
    MAX_PROCESS = 500

    RETURN_LIMIT = 10
    SCORE_FILTER = 0.000

    CORNET_URL = 'http://cornet-backend:7777/'

    FIRST_POOL_SIZE = 10

    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DB_USER = os.getenv('DB_USER')
    DB_DATABASE = os.getenv('DB_DATABASE')
    DB_PORT = os.getenv('DB_PORT')
    DB_HOST = os.getenv('DB_HOST')

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

    HF_TOKEN = os.getenv('HF_TOKEN')

    SLEEP_M = 0
    SLEEP_P = 0

    SEED_URLS = [
        ["https://en.wikipedia.org/wiki/Information_retrieval"],
        ["https://en.wikipedia.org/wiki/Computer_science"],
        ["https://en.wikipedia.org/wiki/Electrical_engineering"],
        [
            "https://eecs.berkeley.edu",
            "https://cs.stanford.edu",
            "https://eecs.mit.edu",
            "https://cs.cmu.edu",
            "https://cs.harvard.edu",
            "https://cs.princeton.edu",
            "https://cs.cornell.edu",
            "https://cs.ucla.edu",
            "https://cs.washington.edu",
            "https://cs.illinois.edu",
            "https://cse.ucsd.edu",
            "https://cms.caltech.edu",
            "https://cs.ox.ac.uk",
            "https://cst.cam.ac.uk"
        ],
        [
            "https://arxiv.org/archive/cs",
            "https://dl.acm.org",
            "https://ieeexplore.ieee.org",
            "https://dblp.org",
            "https://paperswithcode.com",
            "https://openreview.net",
            "https://www.semanticscholar.org",
            "https://scholar.google.com",
            "https://github.com",
            "https://www.kaggle.com",
            "https://news.ycombinator.com"
        ]


    ]

    CRAWL_THREAD_COUNT = 5
    PROCESS_THREAD_COUNT = 5
    assert len(SEED_URLS) == CRAWL_THREAD_COUNT

    DESIGN_FILE_EXTS = (".png", ".jpg", ".jpeg", ".ico", ".webp", ".svg", ".css", ".docx")