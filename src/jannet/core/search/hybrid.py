import logging

from src.jannet.core.search.lexical_search import LexicalSearch
from src.jannet.core.search.semantic_search import SemanticSearch
from src.jannet.utils.config import Config
from src.jannet.utils.timer_wrapper import timed

logger = logging.getLogger(__name__)


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



    @timed
    def combined_search(self, term):

        def normalize(scores):
            if not scores:
                return {}
            mx = max(scores.values())
            mn = min(scores.values())
            return {doc_id: 1.0 if mx == mn else (score - mn) / (mx - mn) for doc_id, score in scores.items()}

        vector_weight = self.vector_weight
        kw_weight = self.kw_weight
        v_search_instance = self.v_search_instance
        kw_search_instance = self.kw_search_instance

        logger.info("Starting semantic search")
        vector_scores = v_search_instance.search(term)
        logger.info("Semantic search completed")

        logger.info("Starting lexical search")
        keyword_scores = kw_search_instance.search(term)
        logger.info("Lexical search completed")

        k_set = (keyword_scores or {}).keys()
        v_set = (vector_scores or {}).keys()
        all_ids = set(k_set | v_set)

        if len(all_ids) == 0:
            logger.info("No search results found")
            return [], []

        keyword_scores = normalize(keyword_scores)
        vector_scores = normalize(vector_scores)



        logger.info("Combining ranking scores")
        combined_scores = {}
        for doc_id in all_ids:
            kw = keyword_scores.get(doc_id, -1)
            vec = vector_scores.get(doc_id, -1)

            if vec == -1:
                combined_score = kw
            elif kw == -1:

                combined_score = vec
            else:
                combined_score = (kw_weight * kw + vector_weight * vec)
            if combined_score < Config.SCORE_FILTER:
                logger.debug("Filtered document %d", doc_id)
                continue
            combined_scores[doc_id] = combined_score

        logger.info("Score combination completed")

        sorted_ids = sorted(
            combined_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:Config.FIRST_POOL_SIZE][:self.return_limit]
        top_ids = [doc_id for doc_id, _ in sorted_ids]

        all_contents = self.db.get_contents_by_ids(top_ids)



        url_by_id = dict(self.db.get_url_from_ids(top_ids))



        logger.info(
            "Hybrid search '%s': %d lexical, %d semantic, %d total candidates",
            term,
            len(keyword_scores),
            len(vector_scores),
            len(all_ids),
        )

        return_urls = []
        return_contents = []

        for rank, (doc_id, score) in enumerate(sorted_ids, 1):
            url = url_by_id[doc_id]
            kw = keyword_scores.get(doc_id, 0)
            vec = vector_scores.get(doc_id, 0)

            logger.info(
                "#%d %s | final=%.3f kw=%.3f vec=%.3f",
                rank,
                url,
                score,
                kw,
                vec,
            )

            return_urls.append(url)
            return_contents.append(all_contents[doc_id] if doc_id in all_contents else "")

        logger.info("Returning %d results", len(return_urls))

        return return_urls, return_contents
