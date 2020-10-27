'''#purpose:
# to clean all articles from the tvnz and save a clean pickle file for next process

#importing necessary libraries for this code
'''

#STEP 0: import the following packages for running this file
import os
import pandas as pd


#please change the following location

#STEP 1: running all required funcitons for this.
## all Functions to run the above command.

def append_all_tvnz_batches(location):
    '''
    to append all tvnz batches of csv file to create one dataframe
    Input:
        location (str): location where all the batch files for tvnz is stored
    Returns:
        Nothing, it would save a tvnz_raw_data.pkl file
    '''
    all_files = []

    for i in os.listdir(location):
        if 'batch' in i:
            all_files.append(i)

    first_file = pd.read_csv(location + all_files[0], header=None)
    for file in all_files[1:]:
        temp_df = pd.read_csv(location + file, header=None)
        first_file = first_file.append(temp_df)
    first_file = first_file.rename(columns={0: 'date', 1: 'title', 2: 'article', 3:'url'})
    first_file['date'] = first_file['date'].astype('str')
    first_file.to_pickle(location+'tvnz_raw_data.pkl')

    return_message = "all tvnz batches appended"

    return return_message

def clean_tvnz_articles(location, tvnz_unclean_filename):
    '''
    takes a tvnz_unclean pickle object and creates a clean pickle file
    '''
    data = pd.read_pickle(location+tvnz_unclean_filename)
    data['date'] = pd.to_datetime(data['date'], format='%Y%m%d')
    data = data.drop_duplicates(subset='title', keep='first')
    data['newspaper'] = 'tvnz_one_news'
    data['article'] = data['article'].astype('str')

    data.to_pickle('../data/clean/'+'sample_tvnz_clean_data.pkl')

    return data.shape

#STEP 2: Run the following commands to append and clean all data files
#        change the location where all csv files are for tvnz
if __name__ == "__main__":
    print("starts cleaning tvnz scrapped data")
    append_all_tvnz_batches("../data/raw/")
    clean_tvnz_articles("../data/raw/", 'tvnz_raw_data.pkl')
    print("clean tvnz data created")
