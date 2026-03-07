import numpy as np


class PageRank:
    def __init__(self, db):
        def __init__(self, db=None, vdb=None):
            self.db = db
            self.vdb = vdb


        def map_pagerank(self, pairs):
            pages = sorted(set(pair[0] for pair in pairs))

            page_index = {pages: i for i, pages in enumerate(pages)}

            n = len(pages)
            A = np.zeros((n, n))

            for from_url, to_url in pairs:
                i = page_index[from_url]
                j = page_index[to_url]
                A[i][j] = 1

            col_sums = A.sum(axis=0)
            M = A / col_sums



