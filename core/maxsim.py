from managers.db_manager import get_vdb


class MaxSim():
    def __init__(self, final_count, vdb=get_vdb()):
        self.final_count = final_count
        self.vdb = vdb

    def calculate(self, term, contents):

        final_scores = {}
        term_tokens = self.vdb.tokenize_text(term).squeeze(0)
        for url, content in contents.items():

            content_tokens = self.vdb.tokenize_text(content).squeeze(0)
            similarity_matrix = term_tokens @ content_tokens.T
            max_similarities = similarity_matrix.max(dim=1).values
            final_scores[url] = max_similarities.sum().item()

        return final_scores


