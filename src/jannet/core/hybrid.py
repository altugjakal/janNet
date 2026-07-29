import logging

from src.jannet.core.lexical_search import LexicalSearch
from src.jannet.core.semantic_search import SemanticSearch
from src.jannet.utils.config import Config
from src.jannet.core.maxsim import MaxSim
from src.jannet.utils.parsing import html_to_clean, get_tld, get_domain
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
        self.maxsim_instance = MaxSim(vdb=self.vdb)

    def get_tld_rank(self, url, importance):

        domain = get_domain(url)
        tld = get_tld(domain)
        if tld in Config.EDU_TLDS:
            tld_multiplier = Config.EDU_MULT
        elif tld in Config.AUTHORITIVE_TLDS:
            tld_multiplier = Config.AUTHORITIVE_MULT
        else:
            tld_multiplier = Config.GENERIC_MULT

        base_score = importance * tld_multiplier
        return base_score

    @timed
    def combined_search(self, term):
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

        all_contents = self.db.get_contents_by_ids(all_ids)

        clean_sorted_contents = {}

        def normalize(scores):
            if not scores:
                return {}
            mx = max(scores.values())
            mn = min(scores.values())
            if mx == mn:
                return {doc_id: 1.0 for doc_id in scores}
            return {
                doc_id: (score - mn) / (mx - mn)
                for doc_id, score in scores.items()
            }

        keyword_scores = normalize(keyword_scores)
        vector_scores = normalize(vector_scores)

        logger.info("Fetching PageRank scores")
        if Config.PAGERANK_CALCULATION:
            pagerank_scores = self.db.get_pagerank_scores_batch(all_ids)
        logger.info("PageRank fetch completed")

        logger.info("Combining ranking scores")
        combined_scores = {}
        for doc_id in all_ids:
            kw = keyword_scores.get(doc_id, 0)
            vec = vector_scores.get(doc_id, 0)
            pr = pagerank_scores.get(doc_id, 0) if Config.PAGERANK_CALCULATION else 0

            if kw + vec < Config.SCORE_FILTER:
                logger.debug("Filtered document %d", doc_id)
                continue

            combined_score = (kw_weight * kw + vector_weight * vec) * (1 + pr)
            combined_scores[doc_id] = combined_score

        logger.info("Score combination completed")

        sorted_urls = sorted(
            combined_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:Config.FIRST_POOL_SIZE]

        for doc_id, score in sorted_urls:
            try:
                clean_sorted_contents[doc_id] = html_to_clean(all_contents[doc_id])
                logger.debug("Prepared document %d for MaxSim", doc_id)
            except KeyError:
                logger.warning("Missing content for document %d", doc_id)
                continue

        logger.info("Starting MaxSim reranking")
        maxsim_scores = self.maxsim_instance.calculate(term, clean_sorted_contents)
        logger.info("MaxSim reranking completed")

        id_by_url = {}
        final_scores_by_url = {}

        for doc_id, url in self.db.get_url_from_ids(maxsim_scores.keys()):
            id_by_url[url] = doc_id
            final_scores_by_url[url] = maxsim_scores[doc_id]

        final_sorted_urls = sorted(
            final_scores_by_url.items(),
            key=lambda x: self.get_tld_rank(x[0], x[1]),
            reverse=True
        )

        logger.info(
            "Hybrid search '%s': %d lexical, %d semantic, %d total candidates",
            term,
            len(keyword_scores),
            len(vector_scores),
            len(all_ids),
        )

        return_urls = []
        return_contents = []

        for rank, (url, score) in enumerate(final_sorted_urls, 1):
            doc_id = id_by_url[url]
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
            return_contents.append(all_contents[doc_id])

        logger.info("Returning %d results", len(return_urls))

        return return_urls, return_contents