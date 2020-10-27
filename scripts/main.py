
"""
Purpose: Main file that appends the clean (downloaded) dataframes
and creates an Economic Policy Uncertainty Index for New Zealand.

Additional indices are created for the following categories:
Natural Disasters
Domestic Violence

@authors: diego - rukshan - piyush
"""

from datetime import datetime
import glob
import pandas as pd
import matplotlib.pyplot as plt
import index_builder as ib


def append_dfs_in_dir(dir_of_dfs):
    '''
    Appends the dataframes available from each source
    into one dataframe.
        Inputs:
            - dir_of_dfs (str): Directory where the
            dataframes are stored, they must be in
            pickle format
        Returns:
            - df (Pandas dataframe): The appended
            dataframe
    '''

    files = glob.glob(dir_of_dfs)
    df = None

    for i, file in enumerate(files):
        if i == 0:
            df = pd.read_pickle(file)
        else:
            temp_df = pd.read_pickle(file)
            df = df.append(temp_df, sort=False)

    return df


def labels(fig, index_name):

    '''
    Creates annotated labels for the Economic Policy Uncertainty Plot
    had to be positioned manually in the case of EPU
    to capture exact dates and to avoid overwriting labels.

    Inputs:
        fig (instance of plot):
        index_name (str): string of index being labelled.
    Returns:
        None. Saves the updated labelled plot

    '''

    date_min = datetime.strptime("2009-01", "%Y-%m")
    date_max = datetime.strptime("2020-03", "%Y-%m")

    plt.xlim(date_min, date_max)
    plt.ylim(0, 0.023)

    date = datetime.strptime("2009-03", "%Y-%m")
    fig.annotate('Global Financial Crisis', rotation=0, va="center",  \
        ha="left", xy=(date, 0.016), xytext=(date, 0.019),  \
        arrowprops=dict(arrowstyle="->", relpos=(0.5, 1)))

    date = datetime.strptime("2010-02", "%Y-%m")
    fig.annotate('Euro-zone\nCrisis', rotation=0, va="top",  \
        ha="left", xy=(date, 0.013), xytext=(date, 0.017),  \
        arrowprops=dict(arrowstyle="->", relpos=(0.5, 1)))

    date = datetime.strptime("2011-02", "%Y-%m")
    fig.annotate('Christchurch\nEarthquake', rotation=0, va="top",  \
        ha="center", xy=(date, 0.009), xytext=(date, 0.013),  \
        arrowprops=dict(arrowstyle="->", relpos=(0.5, 1)))

    date = datetime.strptime("2014-09", "%Y-%m")
    fig.annotate('51st General\nElections', rotation=0, va="top",  \
        ha="center", xy=(date, 0.005), xytext=(date, 0.008),  \
        arrowprops=dict(arrowstyle="->", relpos=(0.5, 1)))

    date = datetime.strptime("2016-06", "%Y-%m")
    fig.annotate('Brexit\nReferendum', rotation=0, va="top",  \
        ha="center", xy=(date, 0.008), xytext=(date, 0.011),  \
        arrowprops=dict(arrowstyle="->", relpos=(0.5, 1)))

    date = datetime.strptime("2017-09", "%Y-%m")
    fig.annotate('52nd General\nElections', rotation=0, va="top",  \
        ha="center", xy=(date, 0.014), xytext=(date, 0.017),  \
        arrowprops=dict(arrowstyle="->", relpos=(0.5, 1)))

    date = datetime.strptime("2019-03", "%Y-%m")
    fig.annotate('Mosque\nShooting', rotation=0, va="top",  \
        ha="center", xy=(date, 0.012), xytext=(date, 0.015),  \
        arrowprops=dict(arrowstyle="->", relpos=(0.5, 1)))

    date = datetime.strptime("2019-09", "%Y-%m")
    fig.annotate('5-year low\neconomic growth', rotation=0, va="top",  \
        ha="center", xy=(date, 0.019), xytext=(date, 0.022),  \
        arrowprops=dict(arrowstyle="->", relpos=(0.5, 1)))

    date = datetime.strptime("2020-01", "%Y-%m")
    fig.annotate('Corona\nVirus\nOutbreak', rotation=0, va="center",  \
        ha="left", xy=(date, 0.013), xytext=(date, 0.015),  \
        arrowprops=dict(arrowstyle="->", relpos=(1, 1)))

    plt.savefig('../figures/' + index_name + '.png', dpi=600)



def main():
    '''
    Main function that creates an index and plot for each of the
    following categories (for New Zealand). Uses the clean downloaded
    dataframes.

    Economic Policy Uncertainty (EPU)
    Natural Disasters
    Domestic Violence
    '''

    print("Appending clean dataframes for each news source")
    df_total = append_dfs_in_dir('../data/clean/*pkl')

    #FOR ECONOMIC POLICY UNCERTAINTY
    print("Index: Economic Policy Uncertainty (EPU)")
    policy = ib.NewspaperIndex(df_total, 'EPU', ['econ', 'policy', 'uncert'])
    print("EPU Index created")
    fig = policy.plot_index(2009)
    print("Plot Saved: figures/EPU.png")
    labels(fig, 'EPU')

    #POTENTIAL: FOR NATURAL DISASTERS
    print("Index: Natural Disasters")
    natural_disasters = ib.NewspaperIndex(df_total, 'Natural Disaster', ['earthquake', 'damage'])
    print("Natural Disaster Index created")
    fig = natural_disasters.plot_index(2009)
    print("Plot Saved: figures/Natural Disasters.png")

    #POTENTIAL: FOR DOMESTIC VIOLENCE
    print("Index: Domestic Violence")
    dom_viol = ib.NewspaperIndex(df_total, 'Domestic Violence', ['domestic', 'violence'])
    print("Domestic Violence Index created")
    fig = dom_viol.plot_index(2009)
    print("Plot Saved: figures/Domestic Violence.png")

if __name__ == "__main__":
    main()
