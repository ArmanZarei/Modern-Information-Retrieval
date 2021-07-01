import numpy as np
import json
import pandas as pd


def get_paper_subject_vec(papers, subjects):
    for paper in papers:
        paper['related_topics'] = list(set([topic.lower() for topic in paper['related_topics']]))
    return np.array([[1 if sub in paper['related_topics'] else 0 for sub in subjects] for paper in papers])


def pearson_sim(a, b):
    return np.sum((a-a.mean()) * (b-b.mean())) / (np.sqrt(np.sum((a-a.mean())**2)) * np.sqrt(np.sum((b-b.mean())**2)))


def get_recommendation_list(papers, users_df, user_idx, result_count, N):
    user_row = users_df.iloc[user_idx]
    user_not_nan_columns_mask = ~user_row.isna()
    users_df.drop(user_idx, inplace=True)

    columns_to_fill = users_df.columns[~user_not_nan_columns_mask]
    for column_to_fill in columns_to_fill:
        similar_users = []
        for index, row in users_df.iterrows():
            if np.isnan(row[column_to_fill]):
                continue
            row_not_nan_columns_mask = ~row.isna()
            if np.any(user_not_nan_columns_mask & row_not_nan_columns_mask):
                common_columns_mask = user_not_nan_columns_mask & row_not_nan_columns_mask
                similarity = pearson_sim(user_row[common_columns_mask], user_row[common_columns_mask])
                similar_users.append({
                    "similarity": similarity,
                    "score": similarity*(row[column_to_fill] - row[common_columns_mask].mean())
                })

        if len(similar_users) == 0:
            continue

        similar_users = sorted(similar_users, key=lambda item: -item['similarity'])
        most_similar_ones = similar_users[:min(len(similar_users), N)]

        predict = user_row[user_not_nan_columns_mask].mean() + sum([u['score'] for u in most_similar_ones]) / sum([u['similarity'] for u in most_similar_ones])
        user_row[column_to_fill] = predict
    
    
    # ------ Get Best Result that fits the user profile ------ #
    user_row.fillna(0, inplace=True)
    papers_vec = get_paper_subject_vec(papers, [sub.lower() for sub in users_df.columns])
    
    papers_norm_vec = np.linalg.norm(papers_vec, axis=1)
    papers_norm_vec[papers_norm_vec == 0] = 1
    normalized_papers_vec = papers_vec / papers_norm_vec[:, np.newaxis]
    
    user_vec = user_row.to_numpy()
    normalized_user_vec = user_vec / np.linalg.norm(user_vec)
    
    result = [papers[i] for i in np.argsort(normalized_papers_vec @ normalized_user_vec.T)[::-1][:result_count]]

    return user_row.to_numpy()/user_row.to_numpy().sum(), result 

