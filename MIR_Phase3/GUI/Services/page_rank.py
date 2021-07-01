import json
import numpy as np


def calculate_page_rank(papers, alpha, X_diff_threshold=1e-15):
    paper_id_to_idx, idx_to_paper_id = {}, {}
    for idx, paper in enumerate(papers):
        paper_id_to_idx[paper['id']] = idx
        idx_to_paper_id[idx] = paper['id']

    N = len(papers)
    P = np.zeros((N, N))
    for i, paper in enumerate(papers):
        refrences_idx = list(map(lambda p_id: paper_id_to_idx[p_id], [ref for ref in paper['references'] if ref in paper_id_to_idx]))
        if len(refrences_idx) == 0:
            P[i, :] = 1/N
        else:
            P[i, refrences_idx] = 1/len(refrences_idx)
    V = np.ones(N)
    P = (1-alpha)*P + alpha*V/N

    X = np.zeros(N)
    X[np.random.randint(N)] = 1
    while True:
        X_tmp = X @ P
        if (X_tmp - X < X_diff_threshold).all():
            break
        X = X_tmp

    indices = np.argsort(X)[::-1]

    return {idx_to_paper_id[idx]: X[idx] for idx in indices}
