import pandas as pd
import json
import numpy as np


def get_paper_subject_vec(papers, subjects):
    for paper in papers:
        paper['related_topics'] = set([topic.lower() for topic in paper['related_topics']])
    return np.array([[1 if sub in paper['related_topics'] else 0 for sub in subjects] for paper in papers])


def get_recommendation_list(papers, users_df, user_idx, result_count):
    users_df.fillna(0, inplace=True)
    papers_vec = get_paper_subject_vec(papers, [sub.lower() for sub in users_df.columns])
    
    papers_norm_vec = np.linalg.norm(papers_vec, axis=1)
    papers_norm_vec[papers_norm_vec == 0] = 1
    normalized_papers_vec = papers_vec / papers_norm_vec[:, np.newaxis]
    
    user_vec = users_df.iloc[user_idx].to_numpy()
    normalized_user_vec = user_vec / np.linalg.norm(user_vec)
    
    result = [papers[i] for i in np.argsort(normalized_papers_vec @ normalized_user_vec.T)[::-1][:result_count]]

    return result


if __name__ == '__main__':
    users_df = pd.read_csv("../data.csv")
    with open('../CrawledPapers.json') as json_file:
        papers = json.load(json_file)
    print([paper['id'] for paper in get_recommendation_list(papers, users_df, 0, 10)])
