""" 
Computes the cumulative sum of the most common verbs and prepositions, then plot it
Author: Fernando Casabán Blasco
"""

import pandas as pd
import json
import matplotlib.pyplot as plt
import numpy as np
plt.style.use('ggplot')

VERBS_FILE_PATH = "results/stats/simple_sentences_common_verbs.json"
PREPOSITIONS_FILE_PATH = "results/stats/simple_sentences_common_prep.json"
SAVE_PATH = "results/"

def get_cumsum_df(json_file):
    """ Reads a json file with a Counter dict and returns a dataframe with the info read and the cumsum of the count """
    with open(json_file) as jfile:
        dict = json.load(jfile)
    df = pd.DataFrame(dict.items(), columns=["elem","count"])
    df["cumsum"] = df["count"].cumsum() / df["count"].sum()
    return df

def plot_cumsum(df, tick_freq=20, topic = "Elem", save_plots=False):
    """ Function to plot the elements index(x) and cumsums (y) to check how many elements to choose"""
    df[["elem","cumsum"]].plot()
    xticks = np.arange(0, len(df)+1, tick_freq)
    plt.xticks(xticks, rotation="vertical")  
    plt.title(f"Cumulative sum for {topic}")
    plt.xlabel(f"{topic} (index)")
    plt.ylabel("% Cases covered")
    if save_plots:
        plt.savefig(f"{SAVE_PATH}cumsum_{topic}.png".lower(),  dpi=300,bbox_inches='tight')
    plt.show()

def plot_cumsum_labels(df, tick_freq=20, topic = "Elem", save_plots=False):
    """ Function to plot the elements text (x) and cumsums (y) to check how many elements to choose"""
    labels = df["elem"]
    df = df.set_index("elem")
    ts = df["cumsum"]
    ts.plot()
    xticks = np.arange(0, len(df), tick_freq)
    print(xticks)
    labels = labels[xticks]
    plt.xticks(xticks, labels, rotation=45)
    plt.title(f"Cumulative sum for {topic}")
    plt.xlabel(f"{topic} (index)")
    plt.ylabel("% Cases covered")
    if save_plots:
        plt.savefig(f"{SAVE_PATH}cumsum_{topic}_top.png".lower(),  dpi=300)
    plt.show()


def main():
    verbs = get_cumsum_df(VERBS_FILE_PATH)
    prepositions = get_cumsum_df(PREPOSITIONS_FILE_PATH)
    print(sum(verbs["count"]))
    verbs = verbs[:10]
    #plot_cumsum_labels(verbs, tick_freq=1, topic = "Elem", save_plots=True)
    plot_cumsum(verbs, tick_freq=25, topic="Verbs", save_plots=False)
    plot_cumsum(prepositions, tick_freq=10, topic="Prepositions", save_plots=False)
    print(verbs.head(30))

if __name__ == "__main__":
    main()