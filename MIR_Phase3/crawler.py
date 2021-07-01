from typing import cast
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import re
import time
import json
from tqdm import tqdm
import sys
import traceback
    
class MicrosoftAcademicCrawler:
    def __init__(self, driver, seed_urls, limit_count=2000, sleep_duration=4, loading_time_limit=10, number_of_try_if_fail=2):
        self.driver = driver
        self.queue = seed_urls
        self.visited_ids = set([self.__get_paper_id_from_url(url) for url in seed_urls])
        self.limit_count = limit_count
        self.sleep_duration = sleep_duration
        self.loading_time_limit = loading_time_limit
        self.number_of_try_if_fail = number_of_try_if_fail
    
    def __get_paper_id_from_url(self, url):
        return int(re.findall(r"\d+", url)[-1])
    
    def __get_next_paper(self):
        url = self.queue.pop(0)
        return self.__get_paper_id_from_url(url), url

    def __find_element(self, selector):
        return WebDriverWait(self.driver, self.loading_time_limit).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
        )

    def __find_elements(self, selector):
        return WebDriverWait(self.driver, self.loading_time_limit).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector))
        )

    def __add_references_url_to_queue(self, refrences):
        for ref in refrences:
            p_id = self.__get_paper_id_from_url(ref)
            if p_id not in self.visited_ids:
                self.visited_ids.add(p_id)
                self.queue.append(ref)

    def __extract_paper_information(self, paper_id):
        self.__find_element('.ma-paper-results')
        paper = {
            'id': paper_id,
            'title': self.__find_element('.name-section .name').text,
            'abstract': self.__find_element('.name-section > p').text,
            'date': int(self.__find_element('.name-section .publication .year').text),
            'authors': [author for author in map(lambda d: d.text, self.__find_elements('.name-section .authors .author-item a:nth-of-type(1)')) if author != ''],
            'related_topics': list(map(lambda d: d.text, self.__find_elements('.name-section .tag-cloud .ma-tag .text'))),
            'citation_count': int(self.__find_element('.name-section .ma-statistics-item[aria-label="Citations"] .data .count').text.replace(",", "")),
            'reference_count': int(self.__find_element('.name-section .ma-statistics-item[aria-label="References"] .data .count').text.replace(",", "")),
            'references': [self.__get_paper_id_from_url(e.get_attribute('href')) for e in self.__find_elements('.ma-paper-results .primary_paper a.title')]
        }
        
        return paper
    
    def crawl(self):
        papers = []
        try_count = {}
        failed_jobs_log = []
        with tqdm(total=self.limit_count) as pbar:
            while len(papers) < self.limit_count and len(self.queue) > 0:
                try:
                    paper_id, paper_url = self.__get_next_paper()

                    if paper_id not in try_count:
                        try_count[paper_id] = -1
                    try_count[paper_id] += 1
                    if try_count[paper_id] > self.number_of_try_if_fail:
                        continue

                    self.driver.get(paper_url)
                    papers.append(self.__extract_paper_information(paper_id))
                    self.__add_references_url_to_queue([e.get_attribute('href') for e in self.__find_elements('.primary_paper a.title')])

                    pbar.update(1)
                    time.sleep(self.sleep_duration)
                except Exception as exception:
                    self.queue.insert(0, paper_url)

                    ex_type, _, ex_traceback = sys.exc_info()
                    stack_trace = ["File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]) for trace in traceback.extract_tb(ex_traceback)]
                    failed_jobs_log.append({
                        'url': paper_url,
                        'exception': {
                            'Type': ex_type.__name__,
                            'Stack Trace': stack_trace
                        }
                    })
        
        return papers, failed_jobs_log

if __name__ == '__main__':
    driver = webdriver.Chrome()
    with open('./start.txt', 'r') as f:
        seed_urls = [l.strip() for l in f.readlines()]
    crawler = MicrosoftAcademicCrawler(driver=driver, seed_urls=seed_urls, limit_count=2,
                                       sleep_duration=4, loading_time_limit=40, number_of_try_if_fail=1)
    papers, failed_jobs_log = crawler.crawl()
    with open('CrawledPapers.json', 'w') as json_file:
        json.dump(papers, json_file, indent=4)
    with open('FailedJobsLog.json', 'w') as json_file:
        json.dump(failed_jobs_log, json_file, indent=4)
    driver.close()
