from utils.misc import make_request
from utils.regex import get_domain, get_tld
from utils.misc import extract_keywords
from utils.data_handling import *
from utils.misc import rank

class Search():
    def __init__(self):
        pass

    def search(self, term):
        terms = extract_keywords(term)

        results = []

        url_scores = {}
        contents = {}

        initials = search_index(terms)

        for url, importance in initials.items():

            try:
                contents[url] = make_request(url).text
            except:
                print("Failed request for content on: Keyword Search, For: ", url)
                continue

            base_score = rank(url, importance)

            if url in url_scores:

                url_scores[url] += base_score
            else:
                url_scores[url] = base_score





        return url_scores, contents