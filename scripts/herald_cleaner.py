# -*- coding: utf-8 -*-
"""

@author: diego - rukshan - piyush
"""

from datetime import datetime
import re
import pandas as pd
import nltk
from nltk.corpus import stopwords

###GLOBAL VARIABLES FOR COLUMN NAMES
NEWSPAPER = "newspaper"
URL = "url"
DATE = "date"
TITLE = "title"
ARTICLE = "article"

def clean_herald(data_frame):
    '''
    Cleans the dataframe. For the Herald this process involves
    eliminating article and date rows that contain
    Nones or are empty. Eliminating all not alphabet
    characters from the articles, converting to lower
    case, and transforming the date to a datetime object
    for easier manipulation
    Inputs:
        - data_frame (Pandas dataframe): Dataframe with
            5 columns: 'newspaper', 'url', 'date', 'title',
            and 'article'.
    '''
    data_frame = data_frame[data_frame[ARTICLE] != 'None']
    data_frame = data_frame[data_frame[ARTICLE] != '']

    #removing premium articles that we are not able to access completely
    data_frame = data_frame[data_frame[DATE] != 'None']
    data_frame = data_frame[data_frame[DATE] != '']

    #cleaning articles from non-letter characters
    data_frame[ARTICLE] = data_frame.apply(lambda x: re.sub("[^a-z ']+", "",\
      x[ARTICLE].lower()), axis=1)
    data_frame[TITLE] = data_frame.apply(lambda x: re.sub("[^a-z ']+", "",\
      x[TITLE].lower()), axis=1)

    #transforming dates to datetime objects
    data_frame[DATE] = data_frame.apply(lambda x: datetime.strptime(\
              x[DATE].strip(), '%d %b, %Y %I:%M%p'), axis=1)

    return data_frame


def remove_stopwords(data_frame, column_name):
    '''
    Removes english stopwords from a single column
    Inputs:
        - data_frame (Pandas dataframe): Dataframe to remove
        stops words from in a given column
        - column_name (str): Column name to remove
        stopwords from
    '''
    stop = stopwords.words('english')
    data_frame[column_name] = data_frame[column_name].apply(lambda x: ' '.\
      join([word for word in x.split() if word not in stop]))
    return data_frame

def main():
    '''
    Runs cleaner on sample data frame produced by herald_crawler.py
    '''
    print("Cleaning sample database created by herald_crawler.py")
    try:
        file_path = "../data/raw/herald_sample.pkl"
        data_frame = pd.read_pickle(file_path)
        data_frame = clean_herald(data_frame)
        nltk.download('stopwords')
        data_frame = remove_stopwords(data_frame, ARTICLE)
        print("Printing 5 first rows")
        print(data_frame.head())
        print("Saving clean dataframe:")
        data_frame.to_pickle("../data/clean/herald_clean_sample.pkl")
        

    except FileNotFoundError:
        print("File not found, please run herald_crawler.py first")

if __name__ == "__main__":
    main()
