'''
Author       : Outsider
Date         : 2023-12-20 10:48:49
LastEditors  : Outsider
LastEditTime : 2023-12-21 15:08:12
Description  : In User Settings Edit
FilePath     : \thesis\backend\ml\msc.py
'''
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN, KMeans
from sklearn.cluster import MeanShift, estimate_bandwidth
from sklearn import metrics
from sklearn.metrics import silhouette_score
from sklearn.metrics import davies_bouldin_score

if __name__ == "__main__":

    df = pd.read_csv('data/anon.csv', delimiter='|')
    columns = set([
        c for c in df.columns if 'perc' in c.lower() or 'log10' in c.lower()
    ]).difference(["POSIX_LOG10_agg_perf_by_slowest"])

    print(df[list(columns)])

    clusters_array = []
    silh_score = []
    dbi_score = []
    ch_score = []
    es = []

    qs = [0.3, 0.8, 1.0]

    for e in qs:

        bandwidth = estimate_bandwidth(df[list(columns)], quantile=e)

        # 使用 Meanshift 聚类算法
        meanshift = MeanShift(bandwidth=bandwidth, n_jobs=8, bin_seeding=True)
        meanshift.fit(df[list(columns)])

        # 获取每个样本的簇标签
        labels = meanshift.labels_

        # 获取簇中心
        cluster_centers = meanshift.cluster_centers_
        clusters_array.append(len(cluster_centers))

        s = silhouette_score(df[list(columns)], labels, metric='euclidean')
        d = davies_bouldin_score(df[list(columns)], labels)
        c = metrics.calinski_harabasz_score(df[list(columns)], labels)
        silh_score.append(s)
        dbi_score.append(d)
        ch_score.append(c)

        print('Done')

    dict = {'clusters': clusters_array, 'silhouette': silh_score}

    df = pd.DataFrame(dict)
    print(df)

    df.to_csv('msc_sil.csv')

    dict = {'clusters': clusters_array, 'dbi': dbi_score}

    df = pd.DataFrame(dict)
    print(df)

    df.to_csv('msc_dbi.csv')

    dict = {'clusters': clusters_array, 'ch': ch_score}

    df = pd.DataFrame(dict)
    print(df)

    df.to_csv('msc_ch.csv')
