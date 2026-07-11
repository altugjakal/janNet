from src.jannet.utils.config import Config
from src.jannet.utils.misc import make_postr, make_getr


class ReverseIndexCommunicator:
    def __init__(self):
        self.index_url = Config.CORNET_URL


    def insert(self, docId, token_map):
        full_url = self.index_url + 'insert'

        structured_map = {
            token: {
                "weight": values[0],
                "position": values[1]

            } for token, values in token_map.items()
        }


        json = {
        "docId": docId,
        "pairs": structured_map,
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






