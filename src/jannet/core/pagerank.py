import traceback

import numpy as np

from src.jannet.managers.db_manager import get_db, get_vdb


class PageRank:
    def __init__(self, db=None, vdb=None, d=0.85, max_iterations=100):
        self.db = db
        self.vdb = vdb
        self.d = d
        self.max_iterations = max_iterations

    #error was caused by the type of score, thanks Mr. Williams
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

        r /= np.max(np.abs(r), axis=0)

        pairs = []
        for i in range(n):
            id = nodes[i]
            score = r[i]
            score = float(score)
            pairs.append((id, score))

        print(pairs[:12])

        try:
            self.db.update_pagerank_batch(pairs)
        except Exception as e:
            traceback.print_exc()


pg = PageRank(db=get_db(), vdb=get_vdb(), d=0.85)
pg.map_pagerank()
