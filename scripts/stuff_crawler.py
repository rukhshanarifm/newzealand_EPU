# -*- coding: utf-8 -*-
"""
Purpose: Using web.archive, collect newspaper articles
for the last 10 years published by New Zealand's leading
newspapers.

Authors:
Diego Diaz
Rukhshan Arif Mian
Piyush Tank
"""

import queue
import re
import csv
from datetime import datetime
from datetime import timedelta
import time
import pandas as pd
from bs4 import BeautifulSoup
import requests

#This link was causing our scraper to stop.
EXCLUDE_ERROR = "worst-case-bushfire-scenario-predicted"

def run(url, start_day, end_day, increment, csv_filename, depth, test=False):
    '''
    Function to run crawler. Collects urls from start_day and end_day and
    stores them in a list. After this, relevant details (title, date, time and
    article text) are extracted from each url.

    Inputs:
        url (string): url
        start_day (int): day to start from (1 means starting from current day
        (today))
        end_day (int): number of days to go back (this value has to be greater
        than or equal to 1)
        increment (int): number of days to increment after one day.
        csv_filename (string): output file's name
        depth (int): depth of web crawling. Number of pages to crawl.
        test (boolean): True if testing, False if not.

    Output:
        List of all URLs that can be news articles.
    '''

    list_of_articles = go_back(url, start_day, end_day, increment, depth)
    make_csv_from_links(list_of_articles, csv_filename, test)

def go_back(url, start_day, end_day, increment, depth):

    '''
    Inputs:
        url (string): url
        start_day (int): day to start from (1 means starting from current day
        (today))
        end_day (int): number of days to go back (this value has to be greater
        than or equal to 1)
        increment (int): number of days to increment after one day.
        depth (int): depth of web crawling. Number of pages to crawl.

    Output:
        List of all URLs that can be news articles.
    '''

    return_set = set()

    while start_day <= end_day:
        #Incrementing the number of days
        #we want to skip
        start_day += increment
        links = crawl(url, depth, start_day)
        return_set.update(links)

    return return_set


def make_csv_from_links(all_links, csv_filename, test=False):
    '''
    Takes a list of articles and creates a csv.

    Input:
        all_links : a list of all links
        csv_filename: filename we want to write to
        test (bool): boolean to indicate if we are testing the code.
        if testing, csv only writes the first 10 articles.

    Ouput:
        None. CSV written to current directory.
    '''

    with open(csv_filename, 'w') as csv_file:
        writer = csv.writer(csv_file, delimiter=",", quoting=csv.QUOTE_MINIMAL)
        counter = 0
        header = ['url', 'title', 'date_time', 'text']
        writer.writerow(header)

        for each_url in all_links:
            each_url = each_url[43:len(each_url)]

            if test:
                if counter == 10:
                    break

            #Error while scraping. Need to exclude it.
            if EXCLUDE_ERROR not in each_url:
                counter += 1
                if counter == 1000:
                    print("Pausing for 30 seconds")
                    time.sleep(30)
                time.sleep(0.2)

                print("Extracting details for Article #", counter)
                details = get_data_from_url(each_url)
                title = details[0]
                date_and_time = details[1]
                text = details[2]
                writer.writerow([each_url, title, date_and_time, text])
            else:
                continue
    print("All valid URLs written to CSV")
    csv_file.close()

def get_articles(soup, starting_url, articles, visited_urls, sites_to_visit):

    '''
    Updates a queue with pages to visit in which to look for news articles while
    adding news articles' urls to a list. This function is meant to work with
    the Stuff.co.nz website.
        Inputs:
            - soup (BeautifulSoup): From the Stuff.co.nz website to search for
                articles and other sites to crawl
            - starting url (str): Domain to stay in
            - articles (list of str): List with urls of newspaper articles to
            visit. The urls are sliced to go straigth to the Herald site instead
            of the site in WebArchive.
            - visited_urls: Dictionary that keeps tracks of visited urls so that
                no site is visited twice
            - sites_to_visit (queue): Queue with urls of sites to crawl for more
                articles and more sites.
        Returns:
            articles:
            sites_to_visit:
    '''

    counter = 0

    for link in soup.find_all('a'):
        counter += 1
        new_url = link.get('href')
        try:
            if is_ok_to_follow(new_url):

                #For relative URLs
                if "/web/" in starting_url and "/web/" in new_url:
                    #Checking if article
                    if check_if_article(new_url):
                        nst_url = starting_url[0:23]
                        link = nst_url + new_url
                        sites_to_visit.put(link)

                #For absolute URLs
                else:
                    if check_if_article(new_url):
                        link = starting_url + new_url
                        sites_to_visit.put(link)

        except:
            print("Unable to scrape url for links")

    return articles, sites_to_visit


def crawl(url, depth, days_back_in_time):
    '''
    Crawler function to crawl webarchive to COLLECT urls.

    Inputs:
        url (string): url
        depth (int): the number of pages to process during the crawl.
        Can be thought of to be the depth of the page. To maintain consistency,
        a depth of 1 was used. That is, the crawler only collected links from
        the first page of the newspaper website.
        days_back_in_time (int): day number that is being crawled.
        1 means current day.
        2 means the day before and so on.
        This is used to create a url in line with webarchive's format.

    Outputs:
        CSV file of the index index.
    '''

    return_list = []
    visited_urls = {}
    article_urls = set([])
    q = queue.Queue()
    counter = 0

    url = get_past_url(url, days_back_in_time)
    req = requests.get(url)
    soup = BeautifulSoup(req.content, "html5lib")
    starting_url = url

    #Adding web.archive.org as a starting URL
    get_articles(soup, 'https://web.archive.org', article_urls, visited_urls, q)

    while not q.empty() and len(visited_urls) < depth:
        url = q.get()

        if visited_urls.get(url):
            continue

        req = requests.get(url)

        if req.status_code != 200:
            continue

        soup = BeautifulSoup(req.content, "html5lib")
        visited_urls[url] = 1
        counter += 1
        ret = get_articles(soup, starting_url, article_urls, visited_urls, q)
        link_list = list(ret[1].queue)
        return_list.extend(link_list)

    return return_list

def get_data_from_url(url):
    '''
    Extract title, text, date and time from a given URL if it
    is an article.
    Input:
        url (string): url
    Output:
        title (string): title of the article
        date_and_time (string): date and time given in the article
        article (string): text of the article
    '''

    try:
        article = ""

        r = requests.get(url)
        soup = BeautifulSoup(r.content, "html5lib")

        #For the purpose of stuff.co.nz, the following div and class combination
        #provide the details of a given article.
        #This further takes care of whether or not the provided link
        #is for a newspaper article.
        divs = soup.find('div', {"class": "sics-component__app__content"})

        #Fetching main text of the article
        article_tags = divs.find_all("p")
        for tag in article_tags:
            article += tag.text

        #Fetching title
        title = soup.find('h1')
        title = title.text

        #Fetching date and time
        date_and_time = soup.find("span",  \
            attrs={"class":"sics-component__byline__date"})
        date_and_time = date_and_time.text

    except:
        title, date_and_time, article = None, None, None

    return title, date_and_time, article

def is_ok_to_follow(url):
    '''
    Checks to see if a URL is alright to follow.

    Input:
    url (string): url

    Ouput:
    True if url alright to follow
    '''
    if url:
        return len(url) > 1 and url[0] == "/"

def get_past_url(url, day_number):
    '''
    As web.archive provided us with previously published articles, this
    function was used to create a past_url. This url is then passed
    into as an increment. Format of web.archive url:
    https://web.archive.org/web/YYYYMMDDHHMMSS/website_url

    Input:
    url (string): url
    day_number (int): the number of day.

    Ouput:
    url with updated date based on web.archive's criteria
    '''

    print("Gathering articles for",  \
        (datetime.today()-timedelta(days=day_number)).strftime('%d-%B-%Y'))
    target_date =  \
    (datetime.today()-timedelta(days=day_number)).strftime('%Y%m%d') +  \
    '013014/'
    return 'https://web.archive.org/web/' + target_date + url

def check_if_article(url):
    '''
    Check to see if a url is a newspaper article.
    For the purpose of https://stuff.co.nz, a link was a
    valid newspaper article if it had 2 cotinuing patterns of
    > 6 digits in it. First was for the YYYYMMDD (>6 digits) in web.archive's
    link and the second was in the https://stuff.co.nz link itself.

    Input:
        url (string): url
    Output:
        True if url is for an article
    '''

    if len(re.findall('\d{6,}', url)) == 2:
        return True

def main():
    '''
    Main function that tests the crawler.
    Goes 3 days back in time and collects newspaper articles from Stuff.co.nz's
    first page and saves them to a .csv (for viewing purposes) and a .pkl.
    For testing purposes, only details for the first 10 articles are saved.
    '''

    print("Starting sample scraping from stuff.co.nz and saving to data/raw")

    list_of_articles = go_back("https://stuff.co.nz", 1, 3, 1, 1)
    make_csv_from_links(list_of_articles,  \
        "../data/raw/test_stuff_raw.csv", test=True)
    return_csv = pd.read_csv("../data/raw/test_stuff_raw.csv")

    print("Creating .pkl file for further processing")
    return_csv.to_pickle("../data/raw/test_stuff_raw.pkl")

if __name__ == "__main__":
    main()
