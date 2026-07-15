import urllib.parse

from src.jannet.utils.config import Config
from src.jannet.utils.misc import make_postr, make_getr


class ReverseIndexCommunicator:
    def __init__(self):
        self.index_url = Config.CORNET_URL


    def insert(self, docId, token_map):
        full_url = self.index_url + 'insert'

        structured_map = {}
        for token, hits in token_map.items():
            structured_map[token] = [
                {
                    "weight": values[0],
                    "position": values[1]
                }
                for values in hits
            ]


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
        dedup_query = set(query)
        full_term = ' '.join(dedup_query)
        encoded_term = urllib.parse.quote(full_term, safe='')
        full_url = self.index_url + f'search/{encoded_term}'
        response = make_getr(full_url)
        return response.json()






