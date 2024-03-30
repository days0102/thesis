'''
Author       : Outsider
Date         : 2023-12-20 10:48:49
LastEditors  : Outsider
LastEditTime : 2023-12-26 09:22:38
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

from vi import variation_of_information

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

    qs = [
        0.001, 0.0025, 0.005, 0.0075, 0.01, 0.015, 0.02, 0.04, 0.06, 0.08, 0.1
    ]

    vi_arrary = []
    last_cluster = None

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

        # 根据聚类结果划分为多个数组
        clusters = {}
        clusters_arrays = []
        columns = list(columns)
        for i, label in enumerate(labels):
            if label not in clusters:
                clusters[label] = len(clusters_arrays)
                clusters_arrays.append([])
            clusters_arrays[clusters[label]].append(tuple(df.loc[i, columns]))

        vi = -1
        if last_cluster is not None:
            vi = variation_of_information(last_cluster, clusters_arrays)

        vi_arrary.append(vi)
        last_cluster = clusters_arrays

        print('Done')

    dict = {'clusters': clusters_array, 'silhouette': silh_score}

    df = pd.DataFrame(dict)
    print(df)

    df.to_csv('out/msc_sil.csv')

    dict = {'clusters': clusters_array, 'dbi': dbi_score}

    df = pd.DataFrame(dict)
    print(df)

    df.to_csv('out/msc_dbi.csv')

    dict = {'clusters': clusters_array, 'ch': ch_score}

    df = pd.DataFrame(dict)
    print(df)

    df.to_csv('out/msc_ch.csv')

    dict = {'clusters': clusters_array, 'vi': vi_arrary}

    df = pd.DataFrame(dict)
    print(df)

    df.to_csv('out/msc_vi.csv')
