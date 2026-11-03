import logging
import math
from collections import defaultdict
from time import time
from math import log1p

from src.jannet.core.process.reverse_index_communicator import ReverseIndexCommunicator
from src.jannet.utils.config import Config
from src.jannet.utils.misc import extract_words
from src.jannet.utils.timer_wrapper import timed

logger = logging.getLogger(__name__)


class LexicalSearch:
    def __init__(self, db):
        self.db = db
        self.ri_client = ReverseIndexCommunicator()

    # optimize tomorrow, plus maybe have lexical pool size included
    @timed
    def search(self, term):

        terms = extract_words(term)


        results = self.ri_client.search(terms)

        id_scores: dict = defaultdict(int)

        for result in results:
            id_scores[result["id"]] = result["bm25Score"]

        return id_scores