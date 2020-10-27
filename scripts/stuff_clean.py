# -*- coding: utf-8 -*-
"""
Purpose: Cleaning data collected from web.archive
Authors:
Diego Diaz
Rukhshan Arif Mian
Piyush Tank
"""

import re
from datetime import datetime
import pandas as pd

URL = "url"
ARTICLE = "article"
TITLE = "title"
DATE = "date"

def clean(raw_data_path, output_filename):

    '''
    Data cleaning. Creating a date_time object, removing
    missing values, duplicates along with lowering text to
    make it consistent.

    Inputs:
        raw_data_path (string): path for raw data
        output_filename (string): filename for output

    Outputs:
        df (dataframe): Cleaned dataframe
    '''

    raw_data_path += ".pkl"
    output_filename += ".pkl"

    stuff_df = pd.read_pickle(raw_data_path)

    stuff_df['newspaper'] = "Stuff"
    stuff_df = stuff_df.rename(columns={"date_time": DATE, "text": ARTICLE})
    stuff_df = stuff_df[['newspaper', URL, DATE, TITLE, ARTICLE]]

    stuff_df = stuff_df[stuff_df[DATE].notnull()]
    stuff_df = stuff_df[stuff_df[ARTICLE].notnull()]
    stuff_df = stuff_df[stuff_df[TITLE].notnull()]
    stuff_df = stuff_df.sort_values(by=ARTICLE).drop_duplicates([URL])

    #Cleaning
    stuff_df[ARTICLE] = stuff_df.apply(lambda x: re.sub("[^a-z ']+", "",  \
        x[ARTICLE].lower()), axis=1)
    stuff_df[TITLE] = stuff_df.apply(lambda x: re.sub("[^a-z ']+", "",  \
        x[TITLE].lower()), axis=1)
    stuff_df[DATE] = stuff_df.date.apply(lambda x: x[7:len(x)])
    stuff_df[DATE] = stuff_df.apply(lambda x:  \
        datetime.strptime(x[DATE].strip(), '%b %d %Y'), axis=1)

    stuff_df = stuff_df.sort_values(by=ARTICLE)
    stuff_df.to_pickle(output_filename)

    print("First five rows of clean dataframe:")
    print(stuff_df.head(5))
    return stuff_df


def main():
    '''
    Main function that cleans sample data that has been collected using
    stuff_crawler.py
    '''

    print("Starting cleaning for stuff.co.nz sample data")
    print("Consolidating variable names and cleaning raw dataset")
    clean("../data/raw/test_stuff_raw", "../data/clean/test_stuff_clean")

if __name__ == "__main__":
    main()
