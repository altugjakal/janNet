from core.search import Search
from core.vector_search import VectorSearch
from utils.config import Config


class HybridSearch():

    def __init__(self, vector_weight=Config.VECTOR_WEIGHT, kw_weight=Config.LEXICAL_WEIGHT, return_limit=5, vdb=None, db=None):
        self.vector_weight = vector_weight
        self.kw_weight = kw_weight
        self.return_limit = return_limit
        self.vdb = vdb
        self.db = db
        self.v_search_instance = VectorSearch(vdb=self.vdb, db=self.db)
        self.kw_search_instance = Search(self.db)

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

            combined_score = kw_weight * kw + vector_weight * vec

            combined_scores[url] = combined_score

        sorted_urls = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
        for url, score in sorted_urls:
            sorted_contents[url] = all_contents[url]

        print(f"\nHybrid search for '{term}' (KW: {kw_weight}, Vec: {vector_weight})")
        print(f"Found: {len(keyword_scores)} keyword, {len(vector_scores)} vector, {len(all_urls)} total")
        print("\nTop results:")
        for i, (url, score) in enumerate(sorted_urls[:return_limit], 1):
            kw = keyword_scores.get(url, 0)
            vec = vector_scores.get(url, 0)
            print(f"{i}. {url}")
            print(f"   Combined: {score:.3f} (KW: {kw:.3f}, Vec: {vec:.3f})")

        return [url for url, score in sorted_urls[:return_limit]], [content for content in list(sorted_contents.values())[:return_limit]]