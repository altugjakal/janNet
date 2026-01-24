from managers.db_manager import get_vdb


class MaxSim():
    def __init__(self, final_count, vdb=get_vdb()):
        self.final_count = final_count
        self.vdb = vdb

    def calculate(self, term, contents):

        final_scores = {}
        print(self.vdb.tokenize_text(term))
        term_tokens = list(self.vdb.tokenize_text(term).values())
        for url, content in contents.items():
            scores = []
            content_tokens = list(self.vdb.tokenize_text(content).values())

            for c in content_tokens:
                for t in term_tokens:
                    similarity = c @ t
                    scores.append(similarity)

            final_scores[url] = max(scores)

        print(final_scores)


