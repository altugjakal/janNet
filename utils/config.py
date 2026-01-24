from dataclasses import dataclass

@dataclass
class Config:
    MODEL = 'nomic-ai/nomic-embed-text-v1.5'
    MODEL_OUTPUT_DIM = 768
    VECTOR_WEIGHT = 0.4
    LEXICAL_WEIGHT = 0.6

    EDU_TLDS = [".edu"]
    AUTHORITIVE_TLDS = [".com", ".net", ".org"]
    AUTHORITIVE_MULT = 1.0
    GENERIC_MULT = 0.7
    EDU_MULT = 2.0
    MAX_CRAWLS = 10000

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
        # ============================================
        # UNIVERSITY HOME PAGES
        # ============================================
        "https://www.stanford.edu/",
        "https://www.mit.edu/",
        "https://www.ox.ac.uk/",
        "https://www.cam.ac.uk/",
        "https://www.princeton.edu/",
        "https://www.columbia.edu/",
        "https://www.berkeley.edu/",
        "https://www.harvard.edu/",
        "https://www.imperial.ac.uk/",
        "https://www.ucl.ac.uk/",
        "https://www.caltech.edu/",
        "https://www.cmu.edu/",

        # ============================================
        # UNIVERSITIES / FACULTY / LABS
        # ============================================
        # Stanford CS - VERIFIED WORKING
        "https://www.cs.stanford.edu/people/faculty",
        "https://www.cs.stanford.edu/people-cs/faculty-research",

        # MIT EECS - VERIFIED WORKING (www.cs.mit.edu redirects/has SSL issues)
        "https://www.eecs.mit.edu/role/faculty/",
        "https://www.eecs.mit.edu/people/",
        "https://www.csail.mit.edu/",

        # Oxford CS - VERIFIED WORKING
        "https://www.cs.ox.ac.uk/people/",
        "https://www.cs.ox.ac.uk/people/faculty.html",

        # Cambridge CS - VERIFIED WORKING
        "https://www.cst.cam.ac.uk/people",
        "https://www.cst.cam.ac.uk/people/directory/faculty",

        # Princeton CS - VERIFIED WORKING (needs /faculty not /people)
        "https://www.cs.princeton.edu/people/faculty",
        "https://www.cs.princeton.edu/",

        # Columbia CS - VERIFIED WORKING
        "https://www.cs.columbia.edu/people/",
        "https://www.cs.columbia.edu/people/faculty/",

        # Berkeley EECS - VERIFIED WORKING
        "https://eecs.berkeley.edu/people/faculty/",
        "https://www2.eecs.berkeley.edu/Faculty/Lists/CS/faculty.html",

        # Harvard CS
        "https://www.seas.harvard.edu/computer-science/people",
        "https://www.seas.harvard.edu/computer-science",

        # Imperial Computing
        "https://www.imperial.ac.uk/computing/people/",
        "https://www.imperial.ac.uk/computing/people/academic-staff/",

        # UCL CS
        "https://www.ucl.ac.uk/computer-science/people",
        "https://www.ucl.ac.uk/computer-science/",

        # Caltech CMS
        "https://www.cms.caltech.edu/people",
        "https://www.cms.caltech.edu/",

        # Carnegie Mellon CS
        "https://www.cs.cmu.edu/people/faculty",
        "https://www.cs.cmu.edu/",

        # ETH Zurich CS
        "https://inf.ethz.ch/people/faculty.html",
        "https://inf.ethz.ch/",

        # University of Washington CSE
        "https://www.cs.washington.edu/people/faculty",
        "https://www.cs.washington.edu/",

        # Georgia Tech Computing
        "https://www.cc.gatech.edu/people/faculty",
        "https://www.cc.gatech.edu/",

        # University of Toronto CS
        "https://web.cs.toronto.edu/people/faculty",
        "https://web.cs.toronto.edu/",

        # ============================================
        # RESEARCH LABS / INSTITUTES
        # ============================================
        "https://www.turing.ac.uk/research",
        "https://ai.stanford.edu/",
        "https://www.csail.mit.edu/research",
        "https://deepmind.google/research/",
        "https://ai.meta.com/research/",
        "https://openai.com/research",
        "https://research.google/",
        "https://www.microsoft.com/en-us/research/",
        "https://www.anthropic.com/research",

        # ============================================
        # PREPRINTS / ACADEMIC REPOSITORIES
        # ============================================
        "https://arxiv.org/list/cs.AI/recent",
        "https://arxiv.org/list/cs.LG/recent",
        "https://arxiv.org/list/cs.CL/recent",
        "https://arxiv.org/list/cs.CV/recent",
        "https://arxiv.org/list/cs.IR/recent",
        "https://arxiv.org/list/cs.RO/recent",
        "https://openreview.net/",
        "https://paperswithcode.com/",
        "https://www.semanticscholar.org/",

        # ============================================
        # CONFERENCES / WORKSHOPS
        # ============================================
        "https://neurips.cc/",
        "https://icml.cc/",
        "https://iclr.cc/",
        "https://aclweb.org/anthology/",
        "https://cvpr.thecvf.com/",
        "https://www.aies-conference.com/",
        "https://aaai.org/",

        # ============================================
        # TECHNICAL BLOGS / THINKERS
        # ============================================
        "https://distill.pub/",
        "https://lilianweng.github.io/",
        "https://karpathy.github.io/",
        "https://colah.github.io/",
        "https://www.lesswrong.com/",
        "https://jalammar.github.io/",
        "https://ruder.io/",
        "https://www.alignmentforum.org/",
        "https://timdettmers.com/",
        "https://www.inference.vc/",

        # ============================================
        # THINK TANKS / POLICY RESEARCH
        # ============================================
        "https://www.brookings.edu/topics/artificial-intelligence/",
        "https://www.rand.org/topics/artificial-intelligence.html",
        "https://www.nber.org/papers",
        "https://cset.georgetown.edu/",
        "https://ainowinstitute.org/",
        "https://futureoflife.org/",

        # ============================================
        # COURSES / LECTURE NOTES
        # ============================================
        "https://cs229.stanford.edu/",
        "https://cs231n.stanford.edu/",
        "https://cs224n.stanford.edu/",
        "https://web.stanford.edu/class/cs224w/",
        "https://www.cs.princeton.edu/courses/",
        "https://www.cl.cam.ac.uk/teaching/",
        "https://www.cs.ox.ac.uk/teaching/",
        "https://ocw.mit.edu/search/?t=Computer%20Science",
        "https://www.fast.ai/",
        "https://d2l.ai/",
        "https://huggingface.co/learn",
    ]

