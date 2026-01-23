from utils.misc import make_request
from utils.misc import extract_keywords
from core.subscore import SubScore

class Search:
    def __init__(self, db):
        self.db = db

    def search(self, term):
        terms = extract_keywords(term)

        results = []

        url_scores = {}
        contents = {}

        initials = self.db.search_index(terms)

        for url, importance in initials.items():

            try:
                contents[url] = make_request(url).text
            except:
                print("Failed request for content on: Keyword Search, For: ", url)
                continue

            base_score = SubScore.get_url_rank(url, importance)


            if url in url_scores:

                url_scores[url] += base_score
            else:
                url_scores[url] = base_score





        return url_scores, contents