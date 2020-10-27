# New Zealand Economic Policy Uncertainty (EPU) 

“But in the end it's only a passing thing, this shadow; even darkness must pass.”
― J.R.R. Tolkien, The Lord of the Rings

### Authors:

Diego Diaz\
Piyush Prafulkumar Tank\
Rukhshan Arif Mian

### Objective
Our objective is to create an economic policy uncertainty (EPU) index for New Zealand. Detailed information about this index can be found in our report. Below are the instructions to run/test our code. 

## Getting Started:
The following instructions will allow you to get a copy of the project on your machine for the purpose of testing.

## Installing: 
Getting the repository:
git clone https://github.com/diodz/new-zealand-epu.git

## Getting data on your machine: 
Our scrapped dataset consists of three files .pkl (one per newspaper) with a combined total of 169,535 newspaper articles, which add up to 528.3 MB. To download, run the following script from the shell, which will also create the required folders: 

$sh get_files.sh 

## Running the tests:
Testing crawlers, data cleaning and creating Index (together):
Run $sh run_all_scripts.sh for the following:

## Downloading the data
Testing crawlers for a small sample of data
Cleaning sample data
Creating the Economic Policy Uncertainty Index using downloaded data

The format of the data is printed while this script runs.


## Testing crawlers separately (for a small sample):
The crawlers took 2 weeks to run in order to scrape all required data (169,500 newspaper articles) for this project. The scripts directory contains the following scripts that scrape a small sample of data for each of the news sources.
	
Set the working directory to scripts and run the following for each news source in the terminal:

python3 herald_crawler.py
python3 stuff_crawler.py
python3 tvnz_crawler.py

The created datasets are not cleaned as they are generated. These are in the .pkl format. A .csv file has been included for stuff.co.nz for the user to look at. 

## Testing data cleaning scripts (for recently created sample):
Data cleaning scripts for each newspaper have been provided. These can be run using the following scripts in the scripts folder:

Set the working directory to scripts and run the following for each news source in the terminal:

python3 herald_cleaner.py
python3 stuff_clean.py
python3 tvnz_clean.py

Run the scripts to perform cleaning of the sample database. The clean sample datasets are saved to /data/clean in .pkl format

## Testing Index Creation and Graphing:
This script creates the Economic Policy Uncertainty Index by using the NewspaperIndex class in scripts/index_builder.py. This can be tested with our full database with the main.py script.

python3 main.py
This script appends the clean (downloaded) dataframes to return a dataframe with 169,500 observations (newspaper articles). These are then used to create an Economic Policy Uncertainty Index using the following keywords:

‘econ’, ‘uncertain’, ‘policy’

A plot for the Economic Policy Uncertainty Index is generated in the figures directory. 

Two additional indices have been created to provide potential for further groundwork. These look at Natural Disasters and Domestic Violence respectively — plots for these can be found in the figures directory as well.

### Built With:

Python 3.7 

#### Acknowledgements:

Professor Lamont Samuels\
Professor Diego Ferrari\
Professor Anne Rogers\
Sinclair Target\
Wanitchaya (Mint) Poonpatanapricha\
Bogdan Alexandru Stoica
