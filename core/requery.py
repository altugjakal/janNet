from utils.timer_wrapper import timed


class Requery:
    def __init__(self, db=None, vdb=None):
        self.db = db
        self.vdb = vdb

    @timed
    def find_similar(self, url):
        document_content = self.db.get_content_by_url(url, limit=4)
        document_content = document_content[0]
        content_vector = self.vdb.vectorise_text(document_content)
        vectors = self.vdb.euclidian_d(content_vector)
        map_s = {}
        url_scores = {}
        url_contents = {}

        vectors = sorted(vectors, key=lambda x: x['score'], reverse=True)
        vector_ids = [v['id'] for v in vectors]
        ids, urls, contents = self.db.get_url_by_vector_id_batch(vector_ids)

        for vector in vectors:
            map_s[vector['id']] = vector['score']

        for id, url, content in zip(ids, urls, contents):

            url_scores[url] = map_s[id]
            url_contents[url] = content


        return [url for url, score in url_scores.items()], [content for content in list(url_contents.values())]

