import urllib
from math import log1p

from core.lexical_search import LexicalSearch
from core.semantic_search import SemanticSearch
from utils.config import Config
from core.maxsim import MaxSim
from utils.regex import html_to_clean, get_tld, get_domain


class HybridSearch:

    def __init__(self, vector_weight=Config.VECTOR_WEIGHT, kw_weight=Config.LEXICAL_WEIGHT,
                 return_limit=Config.RETURN_LIMIT, vdb=None,
                 db=None):
        self.vector_weight = vector_weight
        self.kw_weight = kw_weight
        self.return_limit = return_limit
        self.vdb = vdb
        self.db = db
        self.v_search_instance = SemanticSearch(vdb=self.vdb, db=self.db)
        self.kw_search_instance = LexicalSearch(self.db)
        self.maxsim_instance = MaxSim()

    def get_url_rank(self, url, importance):
        url_obj = urllib.parse.urlparse(url)

        paths = [p for p in url_obj.path.split('/') if p]
        subdomains = url_obj.netloc.split('.')[:-2]
        params = url_obj.query.split('&') if url_obj.query else []

        path_depth = len(paths)
        param_count = len(params)
        subdomain_count = len(subdomains)

        total_depth = path_depth + param_count + subdomain_count

        path_length_penalty = 1 / (1 + max(0, total_depth - 3) * 0.1)

        domain = get_domain(url)
        tld = get_tld(domain)
        if tld in Config.EDU_TLDS:
            tld_multiplier = Config.EDU_MULT
        elif tld in Config.AUTHORITIVE_TLDS:
            tld_multiplier = Config.AUTHORITIVE_MULT
        else:
            tld_multiplier = Config.GENERIC_MULT

        base_score = importance * path_length_penalty * tld_multiplier
        return base_score

    def combined_search(self, term):
        vector_weight = self.vector_weight
        kw_weight = self.kw_weight
        return_limit = self.return_limit
        v_search_instance = self.v_search_instance
        kw_search_instance = self.kw_search_instance

        keyword_scores, keyword_content = kw_search_instance.search(term)
        vector_scores, vector_content = v_search_instance.search(term)

        all_contents = keyword_content | vector_content
        sorted_contents = {}
        clean_sorted_contents = {}

        def normalize(scores):
            if not scores:
                return {}
            mx = max(scores.values())
            mn = min(scores.values())
            if mx == mn:
                return {url: 1.0 for url in scores}
            return {url: (s - mn) / (mx - mn) for url, s in scores.items()}

        keyword_scores = normalize(keyword_scores)
        vector_scores = normalize(vector_scores)

        all_urls = set(keyword_scores.keys()) | set(vector_scores.keys())

        combined_scores = {}
        for url in all_urls:
            kw = keyword_scores.get(url, 0)
            vec = vector_scores.get(url, 0)

            if kw + vec < Config.SCORE_FILTER:
                continue

            combined_score = (kw_weight * kw + vector_weight * vec)

            combined_scores[url] = combined_score

        sorted_urls = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)[:Config.FIRST_POOL_SIZE]
        for url, score in sorted_urls:

            try:
                sorted_contents[url] = all_contents[url]
                clean_sorted_contents[url] = html_to_clean(all_contents[url])
                print(f"Passed: {url}")
            except KeyError:
                print(f"Failed: {url}")
                continue

        maxsim_scores = self.maxsim_instance.calculate(term, clean_sorted_contents)

        final_sorted_contents = {}

        final_sorted_urls = sorted(
            maxsim_scores.items(),
            key=lambda x: self.get_url_rank(x[0], x[1]),
            reverse=True
        )

        for url, score in final_sorted_urls:
            final_sorted_contents[url] = all_contents[url]


        print(f"\nHybrid search for '{term}' (KW: {kw_weight}, Vec: {vector_weight})")
        print(f"Found: {len(keyword_scores)} keyword, {len(vector_scores)} vector, {len(all_urls)} total")
        print("\nTop results:")

        for i, (url, score) in enumerate(final_sorted_urls, 1):
            kw = keyword_scores.get(url, 0)
            vec = vector_scores.get(url, 0)
            print(f"{i}. {url}")
            print(f"   Final Pool Score: {score:.3f} Initial Pool Values: (KW: {kw:.3f}, Vec: {vec:.3f})")

        return [url for url, score in final_sorted_urls], [content for content in list(final_sorted_contents.values())]
