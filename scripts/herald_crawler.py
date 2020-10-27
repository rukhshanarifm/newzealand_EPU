# -*- coding: utf-8 -*-
"""

@author: diego - rukshan - piyush
"""

import queue
import time
from datetime import datetime
from datetime import timedelta
import requests
import pandas as pd
from bs4 import BeautifulSoup

PREFIX_INDEX_WEBARCHIVE = 43

def is_ok_to_follow(url):
    '''
    Checks if the url is a valid relative url
        Input:
            - url (str): Url of website to check
        Returns:
            - boolean
    '''
    return len(url) > 1 and url[0] == "/"

def get_articles(soup, starting_url, articles, visited_urls, sites_to_visit):
    '''
    Updates a queue with pages to visit in which to look for news articles while
    adding news articles' urls to a list. This function is meant to work with
    the NZ Herald website.
        Inputs:
            - soup (BeaitifulSoup): From a Herald website to search for articles
            and other sites to crawl
            - starting url (str): Domain to stay in
            - articles (list of str): List with urls of newspaper articles to
            visit. The urls are sliced to go straigth to the Herald site instead
            of the site in WebArchive.
            - visited_urls: Dictionary that keeps tracks of visited urls so that
            no site is visited twice
            - sites_to_visit (queue): Queue with urls of sites to crawl for more
            articles and more sites.
        Returns:
            None
    '''
    for link in soup.find_all('a'):
        new_url = link.get('href')

        if new_url and is_ok_to_follow(new_url):
            link = starting_url + new_url
            link = link[PREFIX_INDEX_WEBARCHIVE:]
            if link.find("objectid") >= 0:
                articles.add(link)
            elif not link in visited_urls:
                sites_to_visit.put(link)

def get_past_url(url, days_back_in_time):
    '''
    Creates a string with the date of days_back_in_time before than
    today to create a url from an old homepage of the NZ Herald
        Inputs:
            - url (str): Url to visit in a preovious day
            - days_back_in_time (int): Number of days to travel back in
            time in the url
    '''
    target_date = (datetime.today()-timedelta(days=days_back_in_time)).\
    strftime('%Y%m%d') + '013014/'
    return 'https://web.archive.org/web/' + target_date + url


def crawl(num_pages_to_crawl, days_back_in_time, visited_urls):
    '''
    Crawl the college catalog and generates a CSV file with an index.

    Inputs:
        num_pages_to_crawl: the number of pages to process during the crawl
        course_map_filename: the name of a JSON file that contains the mapping
          course codes to course identifiers
        index_filename: the name for the CSV of the index.

    Outputs:
        CSV file of the index index.
    '''

    url = get_past_url('https://www.nzherald.co.nz/', days_back_in_time)
    try:
        req = requests.get(url)#, allow_redirects=False)
    except requests.exceptions.TooManyRedirects:
        print("Too many redirects, skipping url")
        return []
    soup = BeautifulSoup(req.content, features='lxml')
    starting_url = url

    article_urls = set()
    queue_sites = queue.Queue()
    get_articles(soup, 'https://web.archive.org', article_urls, visited_urls,\
                 queue_sites)

    while not queue_sites.empty() and len(visited_urls) < num_pages_to_crawl:

        url = queue_sites.get()
        if visited_urls.get(url):
            continue
        req = requests.get(url)
        if req.status_code != 200:
            continue

        soup = BeautifulSoup(req.content)
        visited_urls[url] = 1
        get_articles(soup, starting_url, article_urls, visited_urls, queue_sites)

    return article_urls


def get_data_from_url(soup):
    '''
    Takes a BeautifulSoup object for a New Zealand Herald article as input
    an returns title, date and time, and the article text as a tuple.
        Inputs:
            - soup (BeautifulSoup): Soup to get newspaper article data from.
            Works for Herald articles.
    '''
    divs = soup.find('div', {"id": "article-body"})#, "class_": ""})
    if divs:
        article_tags = divs.find_all("p")
    else:
        article_tags = None
    article = ""
    if article_tags:
        for tag in article_tags:
            article += tag.text
    title = soup.find('h1')
    if title:
        title = title.text
    date_and_time = soup.find("div", attrs={"class":"publish"})
    if date_and_time and len(date_and_time) > 1:
        date_and_time = list(date_and_time)[0]

    return str(title), str(date_and_time), str(article)


#####
#####
##### The next portion of the code contains functions 
##### to use the scraper for a long period of time
#####
#####

def full_herald_scraping(filename, years_to_scrape, days_to_skip_each_time=1):
    '''
    Will scrape the NZ Herald a number of times equal to 365 times
    years_to_scrape, if days_to_skip_each_time is higher than 1. Saves a
    dataframe with the required columns for the next step of the project.
    Given the long time it takes to scrape a long period, flags are included to
    keep track of the iterations.
        Inputs:
            - filename (str): Filename to save the dataframe into. The output is
            a pandas pickle so it can be saved in .pkl format
            - years_to_scrape (int): Years to scrape from the herald. Increasing
            this number by one will produce 365 more iterations, which takes a
            considerable amount of time.
            - days_to_skip_each_time (int): If something is included in this
            variable, the scraper will skip this amount of days in each
            iteration. This allows to get data that is more spread out in time
            faster.
        Returns:
            None
    '''
    visited_urls = {}
    d_f = pd.DataFrame(columns=["newspaper", "url", "date", "title", "article"])
    counter = 0

    for i in range(0, years_to_scrape * 365):
        count_bad_status = 0
        article_urls = crawl(0, (i + 1) * days_to_skip_each_time, visited_urls)

        for url in article_urls:
            try:
                req = requests.get(url)
            except requests.exceptions.ConnectionError:
                req.status_code = "Connection refused"
                print("Max retries exceeded, connection refused.\
                      Sleeping for thirty seconds before continuing")
                time.sleep(30)
                continue
            if req.status_code != 200:
                print("Bad status code, moving to next article")
                count_bad_status += 1
                continue
            if visited_urls.get(url):
                print("Article already visited")
                continue

            soup = BeautifulSoup(req.content)
            title, date_and_time, article = get_data_from_url(soup)
            visited_urls[url] = 1
            print(title + ": Currently in iteration " + str(i + 1) +\
                  " and date: " + date_and_time)

            d_f.loc[counter] = ["NZ Herald", url, date_and_time, title, article]
            counter += 1
            if counter % 50 == 0:
                d_f.to_pickle(filename)
    d_f.to_pickle(filename)


def sample_herald_scraping(filename):
    '''
    Will scrape two days to test that the scraper works. Saves a dataframe with
    the required columns for the next step of the project.
        Inputs:
            - filename (str): Filename to save the dataframe into. The output is
            a pandas pickle so it can be saved in .pkl format
    '''
    visited_urls = {}
    d_f = pd.DataFrame(columns=["newspaper", "url", "date", "title", "article"])
    counter = 0
    for i in range(3):
        count_bad_status = 0
        article_urls = crawl(0, (i + 1) * 5, visited_urls)
        for url in article_urls:
            try:
                req = requests.get(url)
            except requests.exceptions.ConnectionError:
                req.status_code = "Connection refused"
                print("Max retries exceeded, connection refused. \
                      Sleeping for 10 seconds before continuing")
                time.sleep(10)
                continue
            if req.status_code != 200:
                print("Bad status code, moving to next article")
                count_bad_status += 1
                continue
            if visited_urls.get(url):
                print("Article already visited")
                continue

            soup = BeautifulSoup(req.content, features='lxml')
            title, date_and_time, article = get_data_from_url(soup)
            visited_urls[url] = 1
            print("Saving Article N: " + str(counter) + ", the title is: "+\
                    title + " and date: " + date_and_time)

            d_f.loc[counter] = ["NZ Herald", url, date_and_time, title, article]
            counter += 1
            if counter % 5 == 0:
                print("Max 5 articles per day. Starting new day.")
                break

    print("Finished sample scraping, saved in data/raw")
    d_f.to_pickle(filename)


def main():
    '''
    Runs sample scraper for 3 days and 5 news articles each
    '''
    print("Starting sample scraping from the NZ Herald and saving to data/raw")
    sample_herald_scraping("../data/raw/herald_sample.pkl")

if __name__ == "__main__":
    main()
    #full_herald_scraping("herald_data.csv", 500, 5)
    #continue_scraping("last.csv", 500, 5, 841)
    