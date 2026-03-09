import sys

import numpy as np

from jannet.managers.db_manager import get_db, get_vdb


class PageRank:
    def __init__(self, db=None, vdb=None, d=0.85, max_iterations=100):
        self.db = db
        self.vdb = vdb
        self.d = d
        self.max_iterations = max_iterations


    #db calls are not optimised, this code is here for demonstrational purposes
    def map_pagerank(self):
        pairs = self.db.get_all_link_relation()

        nodes = list({n for edge in pairs for n in edge})
        idx = {node_id: i for i, node_id in enumerate(nodes)}
        n = len(nodes)
        A = np.zeros((n, n))

        for from_url, to_url in pairs:
            i = idx[from_url]
            j = idx[to_url]
            A[j, i] += 1

        col_sums = A.sum(axis=0)

        M = A / np.where(col_sums == 0, 1, col_sums)
        M[:, col_sums == 0] = 1 / n

        n = M.shape[0]
        G = self.d * M + ((1 - self.d) / n) * np.ones((n, n))

        r = np.ones(n) / n

        for _ in range(self.max_iterations):
            r = G @ r

        for i in range(n):
            url = self.db.get_url_by_id(nodes[i])
            print(url, r[i])



pg = PageRank(db=get_db(), vdb=get_vdb(), d=0.85)
pg.map_pagerank()
