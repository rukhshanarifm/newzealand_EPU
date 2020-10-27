'''
# purpose of this code file
# this code is created to crawl TVNZ One news website for it's articles in past and
# save them in a csv ffiles in a batch wise
# the code file is divided in two parts .. Part I, runs the crawlr and Part II
# has all helper function

Authors:
Diego Diaz
Rukhshan Arif Mian
Piyush Tank
'''

# STEP 0: getting required libraries
import datetime
from datetime import datetime
from datetime import timedelta
import queue
import csv
from bs4 import BeautifulSoup
import util
# this crawler uses some function from the util file provided in the PA1.
# so ti would be good required to keep the util.py code file in the same directoty
# to run this crawler


#STEP 1: define all required functions for this crawler

# ALL Functions for this crawler are defined as below and divided ino two parts for
# easier understanding

#PART 1: This part includes the main function to run this crawler

def get_articles_batch_wise(today_url, num_batches, batch_size, days_skip):
    '''
    This is the main cralwer function which takes a url link for tvnz archived website
    and scraps articles from past
    Input:
        today_url (str): web archived link of a particular date, from which past date's
                        articles will be scraped
        num_batches (int): how many batches in past does this crawler needs to go
        batch_size (int): this a number of days in a batch this crawler will scrap articles
                        in one batch. The entir reason to make this batch wise is to make sure
                        that as crawler goes in past , it keeps saving articles, so any potential
                        error does not loose all the data that has been scrapped.
        days_skip (int): number days it skips in each time the crawler goes in past.
                        this is to make sure for our project we have a articles from a
                        distant past.
    '''
    for i in range(num_batches):
        all_links = get_all_articles(today_url, batch_size, 50, days_skip)
        csv_name = "articles_batch_" + str(i) + ".csv"
        make_csv_from_links(all_links, csv_name)
        date = today_url[28:36]
        next_batch_date = get_past_date(date, batch_size*days_skip)
        today_url = "https://web.archive.org/web/" + next_batch_date + '013014/' \
        + 'https://www.tvnz.co.nz/one-news'



#Part 2: All hepler functions for the crawler to work


def crawl_and_get_article_links(num_pages_to_crawl, url_to_crawl):

    '''
    this function finds all urls from the given link and filters links which are
    an article format.
    Inputs:
       num_pages_to_crawl (int): the number of pages to process during the crawl
       url_to_crawl (str): url link, from which all  article links are to be filtered
    Returns:
        article_links (list): a list of  all article links can be found from the given url
    '''
    starting_url = url_to_crawl

    links_queue = queue.Queue()
    links_set = set()
    links_queue.put(starting_url)
    links_set.add(starting_url)
    article_links = set()

    i = 0

    while (i <= num_pages_to_crawl) and (links_queue.qsize() >= 1):

        current_url = links_queue.get()
        soup = cook_soup(current_url)
        #because many times the archive just gives a blank page
        # but does not give a different status_code error, so this is a way
        # to make sure we have a good webpage to crawl
        if not soup:
            continue

       ## to check if this is indeed an article
        if check_if_article(soup):
            article_links.add(current_url)

        new_links = get_all_links(soup, current_url)

        for link in new_links:
            if link not in links_set:
                links_queue.put(link)
                links_set.add(link)
        i += 1
    return list(article_links)

def make_csv_from_links(all_links, csv_filename):
    '''
    takes all links of articles and makes a csv of article dataset
    Input:
        all_links (list) : a list of article links
        csv_filename (str) : a file name with with the articles are to be stored
    '''
    with open("../data/raw/"+csv_filename, 'w') as csv_file:
        writer = csv.writer(csv_file, delimiter=",", quoting=csv.QUOTE_MINIMAL)

        for link in all_links:
            article_link = link[43:]
            soup = cook_soup(article_link)
            if soup:
                title, article_text = get_article_text(soup)
                date = link[28:36]
                print(date)
                print("---------")
                writer.writerow([date, title, article_text, link])
    csv_file.close()

def check_if_article(soup):
    '''
    this function checks if the given link for the tvnz one news, is an article
    format or not.
    Input:
        soup (soup object): soup object of a url
    Returns:
        Boolean : True if the soup is an article, False if not
    '''
    answer = False
    if soup.find_all('div', {'class':'storyPage first-page'}):
        answer = True
    return answer

def get_article_text(soup):
    '''
    This function takes a soup and gives text, title of the article
    Input:
        soup (soup object): soup object of a url
    Returns:
        (title, article_text) (str, str): title of the article and the article
                                        itself
    '''
    meat_of_article = soup.find_all('p')
    title = soup.find('h1').text
    article_text = []
    for para in meat_of_article:
        article_text.append(para.text)
    return (title, article_text)

def get_all_links(soup, url):
    '''
    funcion take a soup object  and will give a list of all relevent urls/links
    for this assignmnet in a list
    Input:
        soup (bs4 object): a bs4 soup object of the wabe page
        url (strl): the url from the bs4 soup was construted,
                    (This is required because to convert into absolute url)
    Output:
        all_links (list): a list of ready to go urls
    '''
    all_links = []

    mega_set = soup.find_all('a')
    for link in mega_set:
        if link.has_attr('href'):
            link = util.remove_fragment(link['href'])
            abs_link = util.convert_if_relative_url(url, link)
            if abs_link not in all_links:
                all_links.append(abs_link)

    return all_links

def cook_soup(url):
    '''
    simple function, takes an url and converts it into a beautiful soup object
    Input:
        url (str): a valid url/link
    Output:
        soup (bs4 object): a bs4 soup object using 'html5lib' parser
    '''
    answer = None
    r_object = util.get_request(url)
    if r_object:
        soup = BeautifulSoup(r_object.content, "html5lib")
        answer = soup
    return answer

def get_past_date(today, days_in_past):
    '''
    gives a day in past
    Input:
        today (str): today;s date in string fromat of YYYYMMDD
        days_in_past (int): number of days in past one wants to go
    Returns:
        past_date (str) : past date in string format
    '''
    yday = datetime.strptime(today, '%Y%m%d') - timedelta(days=days_in_past)
    return yday.strftime('%Y%m%d')

def get_next_link(url, days_skip):
    '''
    takes a web archieved url and gives a past web archieved url
    Input:
        url (str) : web archivec url
        days_skip (int): number of days one wants to go in past
    Returns:
        usable_url (str): past usable url of the web archieved
    '''
    date = url[28:36]
    yday = get_past_date(date, days_skip)
    usable_url = "https://web.archive.org/web/" + yday + '013014/' +\
     'https://www.tvnz.co.nz/one-news'
    return usable_url

def get_all_articles(starting_url, days_in_past, articles_per_page, days_skip):
    '''
    this function geets all artile links for a given range of days in past
    Input:
        starting_url (str): web archied url of the date from which we needs to
                            get more links
        days_in_past (int): number of days in past this part of the code needs
                            to go
        articles_per_page (int): number of articles per url page needs to go
        days_skip (int): the number of days this part of the code needs to
                            skip while going
                        in past
    Returns:
        all_links (list): a list of all artilce links from this function
    '''
    all_links = []
    for i in range(days_in_past):
        url_to_crawl = get_next_link(starting_url, days_skip)
        print(i)
        print(url_to_crawl)
        print("-------------")
        all_article_links = crawl_and_get_article_links(articles_per_page, \
            url_to_crawl)

        all_links += all_article_links

        starting_url = url_to_crawl
    return all_links

def sample_tvnz_scrapping():
    '''
    Will scrape two days to test that the scraper works. Saves a dataframe with the required columns
    for the next step of the project.
    Note: This runs quite slow, will take xx mins to run
    '''
    print("Starting sample scraping from the TVNZ and saving to data/raw")
    today_url = "https://web.archive.org/web/20180507104633/https://www.tvnz.co.nz/one-news"
    get_articles_batch_wise(today_url, num_batches=2,\
     batch_size=2, days_skip=5)
    print("Finished sample scraping, saved in data/raw")



if __name__ == "__main__":
    sample_tvnz_scrapping()
