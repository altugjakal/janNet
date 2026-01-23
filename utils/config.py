from dataclasses import dataclass

@dataclass
class Config:
    MODEL = 'multi-qa-distilbert-cos-v1'
    MODEL_OUTPUT_DIM = 768
    VECTOR_WEIGHT = 0.4
    LEXICAL_WEIGHT = 0.6

    EDU_TLDS = [".edu"]
    AUTHORITIVE_TLDS = [".com", ".net", ".org"]
    AUTHORITIVE_MULT = 1.0
    GENERIC_MULT = 0.7
    EDU_MULT = 2.0

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

    SEED_URLS = crawl_targets = [
        # Universities / Faculty / Labs
        "https://www.cs.stanford.edu/people/faculty",
        "https://www.cs.mit.edu/people/faculty",
        "https://www.cs.ox.ac.uk/people/",
        "https://www.cst.cam.ac.uk/people",
        "https://www.cs.princeton.edu/people",
        "https://www.cs.columbia.edu/people/",
        "https://www.cs.berkeley.edu/people/faculty",
        "https://www.cs.harvard.edu/people/",
        "https://www.imperial.ac.uk/computing/people/",
        "https://www.ucl.ac.uk/computer-science/people",

        # Research Labs / Institutes
        "https://www.turing.ac.uk/research",
        "https://ai.stanford.edu/research",
        "https://www.csail.mit.edu/research",
        "https://deepmind.google/research/",
        "https://ai.meta.com/research/",
        "https://openai.com/research",

        # Preprints / Academic Repositories
        "https://arxiv.org/list/cs.AI/recent",
        "https://arxiv.org/list/cs.IR/recent",
        "https://openreview.net/group?id=NeurIPS.cc",
        "https://openreview.net/group?id=ICLR.cc",
        "https://ora.ox.ac.uk/",
        "https://www.repository.cam.ac.uk/",

        # Conferences / Workshops
        "https://neurips.cc/Conferences/2025/AcceptedPapersInitial",
        "https://icml.cc/Conferences/2025/AcceptedPapersInitial",
        "https://iclr.cc/Conferences/2025/AcceptedPapers",
        "https://aclweb.org/anthology/",

        # Technical Blogs / Thinkers
        "https://distill.pub/",
        "https://lilianweng.github.io/",
        "https://karpathy.github.io/",
        "https://colah.github.io/",
        "https://www.lesswrong.com/",

        # Think Tanks / Policy Research
        "https://www.brookings.edu/topics/artificial-intelligence/",
        "https://www.rand.org/topics/artificial-intelligence.html",
        "https://www.nber.org/papers",

        # Courses / Lecture Notes (high-value, under-crawled)
        "https://cs229.stanford.edu/",
        "https://www.cs.princeton.edu/courses/",
        "https://www.cl.cam.ac.uk/teaching/",
        "https://www.cs.ox.ac.uk/teaching/"
    ]


