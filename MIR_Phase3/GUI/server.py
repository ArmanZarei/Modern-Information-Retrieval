from flask import Flask, render_template, request, send_from_directory, json as fJson
from selenium import webdriver
from Services.crawler import MicrosoftAcademicCrawler
import json
import time
from Services.page_rank import calculate_page_rank
from Services.HITS import calculate_authors_authority
from Services.content_based import get_recommendation_list
import pandas as pd
from Services.collaborative_filtering import get_recommendation_list as cf_get_recommendation_list
from Services.estimate_matrix_missing_values import estimate as matrix_missing_values_estimator


app = Flask(__name__)
app.config['SECRET_KEY'] = 'MIR_PHASE_3_SECRET_KEY'


@app.route('/')
def home():
    return render_template("home.html")


@app.route('/download/<string:filename>')
def download(filename):
    return send_from_directory("./files", filename)


@app.route('/crawler_result', methods=['POST'])
def crawler_result():
    seed_urls = str(request.files["seed_file"].read(), 'utf-8').strip().split('\n')
    count = int(request.form.get('count'))

    driver = webdriver.Chrome()
    crawler = MicrosoftAcademicCrawler(driver=driver, seed_urls=seed_urls, limit_count=count,
                                       sleep_duration=4, loading_time_limit=40, number_of_try_if_fail=1)
    papers, _ = crawler.crawl()
    driver.close()

    result_file_name = 'CrawledPapers-{}.json'.format(str(time.time()))
    with open("./files/"+result_file_name, 'w') as json_file:
        json.dump(papers, json_file, indent=4)

    return render_template(
        'papers_result.html',
        page_title="Crawler Result",
        papers=papers,
        result_file_name=result_file_name,
    )


@app.route('/pagerank_result', methods=['POST'])
def pagerank_result():
    papers = fJson.load(request.files["pagerank_papers_file"])
    alpha = float(request.form.get('alpha'))

    papers_page_rank = calculate_page_rank(papers, alpha)

    result_file_name = 'PageRank-{}.json'.format(str(time.time()))
    with open("./files/" + result_file_name, 'w') as json_file:
        json.dump(papers_page_rank, json_file, indent=4)

    return render_template(
        'pagerank_result.html',
        papers_rank=papers_page_rank,
        result_file_name=result_file_name,
    )


@app.route('/hits_result', methods=['POST'])
def hits_result():
    papers = fJson.load(request.files["hits_papers_file"])
    n = int(request.form.get('hits_result_count'))

    authors_authority = calculate_authors_authority(papers, n)

    result_file_name = 'AuthorsAuthority-{}.json'.format(str(time.time()))
    with open("./files/" + result_file_name, 'w') as json_file:
        json.dump(authors_authority, json_file, indent=4)

    return render_template(
        'hits_result.html',
        authors_authority=authors_authority,
        result_file_name=result_file_name,
    )


@app.route('/recommendation_system/content_based_result', methods=['POST'])
def content_based_result():
    users_df = pd.read_csv(request.files.get('content_based_users_file'))
    papers = fJson.load(request.files["content_based_papers_file"])
    n = int(request.form.get('content_based_result_count'))
    user_idx = int(request.form.get('content_based_user_idx'))

    recommended_papers = get_recommendation_list(papers, users_df, user_idx, n)

    result_file_name = 'ContentBasedRecommendations-{}.json'.format(str(time.time()))
    with open("./files/" + result_file_name, 'w') as json_file:
        json.dump(recommended_papers, json_file, indent=4)

    return render_template(
        'papers_result.html',
        page_title="Recommender System (Content Based) Result",
        papers=recommended_papers,
        result_file_name=result_file_name,
    )


@app.route('/recommendation_system/collaborative_filtering_result', methods=['POST'])
def collaborative_filtering_result():
    users_df = pd.read_csv(request.files.get('collab_filtering_users_file'))
    papers = fJson.load(request.files["collab_filtering_papers_file"])
    result_count = int(request.form.get('collab_filtering_result_count'))
    neighbors_count = int(request.form.get('collab_filtering_neighbors_count'))
    user_idx = int(request.form.get('collab_filtering_user_idx'))

    _, recommended_papers = cf_get_recommendation_list(papers, users_df, user_idx, result_count, neighbors_count)

    result_file_name = 'CollaborativeFilteringRecommendations-{}.json'.format(str(time.time()))
    with open("./files/" + result_file_name, 'w') as json_file:
        json.dump(recommended_papers, json_file, indent=4)

    return render_template(
        'papers_result.html',
        page_title="Recommender System (Collaborative Filtering) Result",
        papers=recommended_papers,
        result_file_name=result_file_name,
    )


@app.route('/recommendation_system/estimate_missing_values', methods=['POST'])
def estimate_missing_values():
    M = pd.read_csv(request.files.get('estimate_missing_values_file'))
    k = int(request.form.get('estimate_missing_values_k'))
    learning_rate = float(request.form.get('estimate_missing_values_learning_rate'))
    steps = int(request.form.get('estimate_missing_values_steps'))

    _, train_error, test_error = matrix_missing_values_estimator(M, k, learning_rate, steps)

    return render_template(
        'missing_values_estimator_result.html',
        train_err=train_error,
        test_err=test_error,
    )


if __name__ == '__main__':
    app.run()
