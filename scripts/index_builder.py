# -*- coding: utf-8 -*-
"""
Purpose: Creates an index based on the given keywords
@authors: diego - rukshan - piyush
"""

import matplotlib.pyplot as plt


###GLOBAL VARIABLES FOR COLUMN NAMES
NEWSPAPER = "newspaper"
URL = "url"
DATE = "date"
TITLE = "title"
ARTICLE = "article"
N_ARTICLES = 'number of articles'

#%%

class NewspaperIndex():
    '''
    The objects from this class are indexes created by
    our methodology based on Baker, Bloom & Davis (2016).
    They estimate the index by counting articles with
    certain keywords in major newspapers.
    '''


    def __init__(self, df, index_name, word_lst):
        '''
        Inputs:
            df (Pandas dataframe): Clean dataframe with
            5 columns: 'newspaper', 'url', 'date', 'title',
            and 'article'. Every column is in string format
            except for date which is a python datetime object
            index_name (str): Name for the index to create
            word_lst (list of strings): List where each
            entry is a keyword to count according to our
            methodology
        '''
        self.index_name = index_name
        self.word_lst = word_lst
        self.group_by = self.make_index(df)


    def make_index(self, df):
        '''
        Creates the index according to our methodology
        requirements. The steps are the following:
            1 - Checks which articles contain the
            provided combination of keywords
            2 - Groups by month and gets the count
            of articles by newspaper
            3 - Divides the total count of articles that contain
            the keywords of each newspaper by the total number
            of articles published by the same newspaper each month
            4 - Calculates a weighted average for each newspaper

            Inputs:
                - df (pandas dataframe): Clean dataframe with
            5 columns: 'newspaper', 'url', 'date', 'title',
            and 'article'. Every column is in string format
            except for date which is a python datetime object

            Returns:
                df (pandas dataframe): Results dataframe with
                a column with the index calculated and a month-year
                column with the month-period.
        '''
        df = has_list_of_words(df.copy(), ARTICLE, self.word_lst, self.index_name)
        df['month_year'] = df[DATE].dt.to_period('M')
        group_by = df.groupby(['month_year', 'newspaper']).agg({self.index_name + ' count':\
                   'sum', ARTICLE:'count'}).rename(columns={ARTICLE:N_ARTICLES})\
                    .reset_index()
        group_by[self.index_name] = group_by[self.index_name\
            + " count"] / group_by[N_ARTICLES]

        counts_by_newspaper = group_by.reset_index().groupby('month_year').agg({N_ARTICLES: 'sum'})\
        .rename(columns={N_ARTICLES:'total articles'})

        new_df = group_by.join(counts_by_newspaper)
        new_df['newspaper weight'] = new_df['total articles'] \
        / new_df[N_ARTICLES]
        new_df['weighted ' + self.index_name] = new_df['newspaper weight']\
        * new_df[self.index_name]

        total_df = new_df.groupby('month_year').agg({self.index_name:'sum', \
                                 }).reset_index()
        return total_df

    def plot_index(self, starting_year):
        '''
        Makes the plot with the index
        Inputs:
            - starting_year (int): Year from which to
            plot the index from
        Outputs:
            - fig (instance): instance of the plot
        '''

        fig = self.group_by[self.group_by['month_year'].dt.year >= starting_year].plot\
        (kind='line', x='month_year', y=self.index_name)
        fig.set_xlabel('Year')
        fig.set_ylabel(self.index_name + ' index')
        fig.spines['top'].set_visible(False)
        fig.spines['right'].set_visible(False)

        plt.legend([self.index_name + ' Index'], loc='upper center')
        plt.savefig('../figures/' + self.index_name + '.png', dpi=600)

        return fig

def has_word(df, column_name, word):
    '''
    Checks if word is present in articles and creates
    a dummy variable with the result
    Inputs:
        - df (Pandas dataframe): Dataframe to remove
        stops words from in a given column
        - column_name (str): Column name to check
        - word (str): Keyword to check
    '''
    df[word] = df[column_name].apply(lambda x: x.count(word) > 0)
    return df


def has_list_of_words(df, column_name, words, index_name):
    '''
    Checks if all words in words are present at the same time
    Inputs:
        - df (Pandas dataframe): Dataframe to remove
        stops words from in a given column
        - column_name (str): Column name to check
        - word (str): Keyword to check
    '''
    df['aux'] = 0
    for word in words:
        df = has_word(df, column_name, word)
        df['aux'] += df[word]
        df = df.drop([word], axis=1)
    df[index_name + ' count'] = df['aux'].apply(lambda x: x == len(words))
    df = df.drop(columns=['aux'], axis=1)

    return df
