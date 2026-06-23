from src.jannet.utils.config import Config
from src.jannet.utils.misc import make_postr, make_getr


class ReverseIndexCommunicator:
    def __init__(self):
        self.index_url = Config.CORNET_URL

    def insert(self, docId, text, base_score):
        full_url = self.index_url + 'insert'
        json = {
        "docId": docId,
        "text": text,
        "score": base_score,
        }

        make_postr(full_url, json)

    def commit(self):
        full_url = self.index_url + 'commit'
        json = {

        }

        make_postr(full_url, json)

    def search(self, query):
        full_url = self.index_url + 'search/'
        full_url = full_url + query

        response = make_getr(full_url)
        return response






