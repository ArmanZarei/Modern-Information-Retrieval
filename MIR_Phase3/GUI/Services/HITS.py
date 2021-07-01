import json
import numpy as np


def calculate_authors_authority(papers, n, HITS_loop_count=5):
    paper_id_to_idx, idx_to_paper_id = {}, {}
    for idx, paper in enumerate(papers):
        paper_id_to_idx[paper['id']] = idx
        idx_to_paper_id[idx] = paper['id']

    author_to_idx, idx_to_author = {}, {}
    author_idx = 0
    for paper in papers:
        for author in paper['authors']:
            if author not in author_to_idx:
                author_to_idx[author] = author_idx
                idx_to_author[author_idx] = author
                author_idx += 1

    N = author_idx
    A = np.zeros((N, N))
    for paper in papers:
        for ref in paper['references']:
            if ref not in paper_id_to_idx:
                continue
            for author_Y in papers[paper_id_to_idx[ref]]['authors']:
                if author_Y not in author_to_idx:
                    continue
                for author_X in paper['authors']:
                    A[author_to_idx[author_X], author_to_idx[author_Y]] = 1

    a, h = np.ones(N), np.ones(N)
    for i in range(HITS_loop_count):
        a, h = A.T @ h, A @ a
        a /= a.sum()
        h /= h.sum()

    indices = np.argsort(a)[:-n-1:-1]

    return {idx_to_author[idx]: a[idx] for idx in indices}

