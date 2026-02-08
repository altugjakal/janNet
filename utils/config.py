class Config:
    MODEL = 'all-distilroberta-v1'
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

            ["https://www.cs.stanford.edu/people-cs"],
            ["https://www.cs.stanford.edu/"],
            ["https://onlinesourcerer.org/"],
            ["https://cs.princeton.edu/"],
            ["https://www.cs.cmu.edu/"],
            ["https://www.cs.berkeley.edu/"],
            ["https://cs.mit.edu/"],
            ["https://www.cs.ox.ac.uk/"],
            ["https://www.cl.cam.ac.uk/"],
            ["https://www.cs.columbia.edu/"],
            ["https://www.cs.utoronto.ca/"]


    ]

    DESIGN_FILE_EXTS = (".png", ".jpg", ".jpeg", ".ico", ".webp", ".svg", ".css", ".docx")
    THREAD_COUNT = 11

    assert len(SEED_URLS) == THREAD_COUNT