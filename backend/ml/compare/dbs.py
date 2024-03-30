'''
Author       : Outsider
Date         : 2023-12-20 10:48:49
LastEditors  : Outsider
LastEditTime : 2023-12-28 08:27:17
Description  : In User Settings Edit
FilePath     : \thesis\backend\ml\dbs.py
'''
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
from sklearn.metrics.cluster import v_measure_score
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
    print(tuple(df.iloc[1]))

    clusters_array = []
    silh_score = []
    dbi_score = []
    ch_score = []
    es = []

    last_labels = None
    vi_arrary = []

    last_cluster = None

    # np.arange(5.0, 10.5, 0.1)
    for e in [5.2,5.3,5.4,5.5,5.6,5.7,5.8,5.9,6.0,6.2,6.4,6.7,7.0,7.8,8.4,9.7,10.3]:

        es.append(e)

        dbscan = DBSCAN(
            min_samples=10,
            eps=e,
            metric='manhattan',
        )

        # Fit the model and predict clusters
        clusters = dbscan.fit(df[list(columns)])
        # 获取聚类标签
        labels = dbscan.labels_

        # 获取簇的数量，排除噪声点（标签为 -1）
        num_clusters = len(set(labels)) - (1 if -1 in labels else 0)
        clusters_array.append(num_clusters)

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


        # 输出聚类标签和簇的数量
        print("DBSCAN Labels:", labels)
        print("Number of Clusters:", num_clusters)

        print('Done')

    dict = {'eps': es, 'clusters': clusters_array, 'silhouette': silh_score}

    df = pd.DataFrame(dict)
    print(df)

    df.to_csv('out/dbs_sil.csv')

    dict = {'eps': es, 'clusters': clusters_array, 'dbi': dbi_score}

    df = pd.DataFrame(dict)
    print(df)

    df.to_csv('out/dbs_dbi.csv')

    dict = {'eps': es, 'clusters': clusters_array, 'ch': ch_score}

    df = pd.DataFrame(dict)
    print(df)

    df.to_csv('out/dbs_ch.csv')

    dict = {'eps': es, 'clusters': clusters_array, 'vi': vi_arrary}

    df = pd.DataFrame(dict)
    print(df)

    df.to_csv('out/dbs_vi.csv')
