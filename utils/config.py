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
    RETURN_LIMIT = 100
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
          "https://www.eecs.mit.edu/",
  "https://cs.stanford.edu/",
  "https://www.cs.cmu.edu/",
  "https://eecs.berkeley.edu/",
  "https://www.cms.caltech.edu/",
  "https://www.cs.cornell.edu/",
  "https://www.cs.princeton.edu/",
  "https://seas.harvard.edu/computer-science",
  "https://cpsc.yale.edu/",
  "https://www.cs.columbia.edu/",
  "https://www.cis.upenn.edu/",
  "https://cs.brown.edu/",
  "https://web.cs.dartmouth.edu/",
  "https://cs.illinois.edu/",
  "https://www.cs.washington.edu/",
  "https://www.cc.gatech.edu/",
  "https://cse.engin.umich.edu/",
  "https://www.cs.ucla.edu/",
  "https://cse.ucsd.edu/",
  "https://www.cs.utexas.edu/",
  "https://www.cs.wisc.edu/",
  "https://www.cs.umd.edu/",
  "https://www.cs.purdue.edu/",
  "https://cs.duke.edu/",
  "https://www.mccormick.northwestern.edu/computer-science/",
  "https://cs.rice.edu/",
  "https://www.cs.jhu.edu/",
  "https://www.cs.virginia.edu/",
  "https://www.csc.ncsu.edu/",
  "https://www.cs.unc.edu/",
  "https://cse.osu.edu/",
  "https://www.cs.rutgers.edu/",
  "https://www.cs.usc.edu/",
  "https://cs.nyu.edu/",
  "https://www.cs.rochester.edu/",
  "https://www.cs.stonybrook.edu/",
  "https://www.cs.bu.edu/",
  "https://www.khoury.northeastern.edu/",
  "https://www.cs.tufts.edu/",
  "https://www.cs.colorado.edu/",
  "https://www.cs.arizona.edu/",
  "https://www.cs.utah.edu/"
    ]
