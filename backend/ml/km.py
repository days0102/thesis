'''
Author       : Outsider
Date         : 2023-12-20 10:48:49
LastEditors  : Outsider
LastEditTime : 2023-12-24 21:37:02
Description  : In User Settings Edit
FilePath     : \thesis\backend\ml\km.py
'''
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN, KMeans
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

    cs = [164, 115, 74, 49, 32, 27, 19, 10, 7, 6, 4]

    vi_arrary = []
    last_cluster = None

    for e in cs:
        clusters_array.append(e)

        km = KMeans(n_clusters=e, random_state=42)

        # Fit the model and predict clusters
        clusters = km.fit(df[list(columns)])
        # 获取聚类标签
        labels = km.labels_

        s = silhouette_score(df[list(columns)], labels, metric='euclidean')
        d = davies_bouldin_score(df[list(columns)], labels)
        c = metrics.calinski_harabasz_score(df[list(columns)], labels)
        silh_score.append(s)
        dbi_score.append(d)
        ch_score.append(c)

        # 根据聚类结果划分为多个数组
        clusters = {}
        clusters_arrays = []
        for i, label in enumerate(labels):
            if label not in clusters:
                clusters[label] = len(clusters_arrays)
                clusters_arrays.append([])
            clusters_arrays[clusters[label]].append(
                tuple(df[list(columns)].iloc[i]))

        vi = -1
        if last_cluster is not None:
            vi = variation_of_information(last_cluster, clusters_arrays)

        vi_arrary.append(vi)
        last_cluster = clusters_arrays

        print('Done')

    dict = {'clusters': clusters_array, 'silhouette': silh_score}

    df = pd.DataFrame(dict)
    print(df)

    df.to_csv('out/km_sil.csv')

    dict = {'clusters': clusters_array, 'dbi': dbi_score}

    df = pd.DataFrame(dict)
    print(df)

    df.to_csv('out/km_dbi.csv')

    dict = {'clusters': clusters_array, 'ch': ch_score}

    df = pd.DataFrame(dict)
    print(df)

    df.to_csv('out/km_ch.csv')

    dict = {'eps': es, 'clusters': clusters_array, 'vi': vi_arrary}

    df = pd.DataFrame(dict)
    print(df)

    df.to_csv('out/km_vi.csv')
