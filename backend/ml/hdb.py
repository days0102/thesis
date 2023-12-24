'''
Author       : Outsider
Date         : 2023-11-29 14:18:49
LastEditors  : Outsider
LastEditTime : 2023-12-20 10:31:27
Description  : In User Settings Edit
FilePath     : \thesis\backend\ml\hdb.py
'''
import pandas as pd
import hdbscan

import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

def load_data(path: str):
    df = pd.read_csv(path, delimiter='|')
    return df


if __name__ == "__main__":
        
    # 折线
    x_1 = [2011,2012,2013,2014,2015,2016,2017]
    y_1 = [58000,60200,63000,71000,84000,90500,107000]
    y_2 = [52000,54200,51500,58300,56800,59500,62700]
    
    #  条形图
    bar_x = ['a','b','c','d']
    bar_y = [20, 10, 30, 25]
    
    # 直方图
    s = np.random.randn(500)
    
    figure,axes = plt.subplots(nrows=1,ncols=2,figsize=(10,5))
    axes[0].plot(x_1,y_1)
    axes[1].bar(bar_x,bar_y)
    
    plt.show()




    df = load_data("data/anon.csv")
    print(df)

    columns = set([
        c for c in df.columns if 'perc' in c.lower() or 'log10' in c.lower()
    ]).difference(["POSIX_LOG10_agg_perf_by_slowest"])

    print(df[list(columns)])

    hdbs = hdbscan.HDBSCAN(min_samples=10,
                           cluster_selection_epsilon=5,
                           metric='manhattan',
                           gen_min_span_tree=True)
    clusterer = hdbs.fit(df[list(columns)])


    plt.figure(figsize=(10, 5))
    clusterer.condensed_tree_.plot(select_clusters=True,selection_palette=sns.color_palette())
    plt.savefig("svae.png")
    plt.show()

    print(clusterer.labels_)
