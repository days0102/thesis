from sklearn.cluster import OPTICS
import hdbscan
from sklearn.datasets import make_blobs
from sklearn.metrics import adjusted_rand_score, silhouette_score, calinski_harabasz_score, davies_bouldin_score
import pandas as pd

# 生成示例数据
df = df = pd.read_csv('posix_sanitize.csv', delimiter=',')
columns = set([
    c for c in df.columns if 'perc' in c.lower() or 'log10' in c.lower()
]).difference(["POSIX_LOG10_agg_perf_by_slowest"])
X = df[list(columns)]

min_samples = [ 2, 3, 4, 5, 6, 7, 8, 9, 10, 20, 30, 40, 50]
min_cluster_size = [2, 3, 4, 5, 6, 7, 8, 9, 10, 20, 30, 40, 50]

df = pd.DataFrame()

for sample, size in zip(min_samples, min_cluster_size):
    # 初始化OPTICS算法
    optics = OPTICS(min_samples=sample, min_cluster_size=size)
    optics_labels = optics.fit_predict(X)

    # 初始化HDBSCAN算法
    hdbscan_labels = hdbscan.HDBSCAN(min_samples=sample,
                                     min_cluster_size=size).fit_predict(X)

    optics_silhouette = silhouette_score(X, optics_labels)
    hdbscan_silhouette = silhouette_score(X, hdbscan_labels)
    calinski_harabasz_optics = calinski_harabasz_score(X, optics_labels)
    calinski_harabasz_hdbscan = calinski_harabasz_score(X, hdbscan_labels)

    davies_bouldin_optics = davies_bouldin_score(X, optics_labels)
    davies_bouldin_hdbscan = davies_bouldin_score(X, hdbscan_labels)

    print(sample, size)
    print(optics_silhouette, hdbscan_silhouette)
    print(calinski_harabasz_optics, calinski_harabasz_hdbscan)
    print(davies_bouldin_optics, davies_bouldin_hdbscan)

    df=df._append({
        'sample': sample,
        'size': size,
        'optics_sil': optics_silhouette,
        'hdbscan_sil': hdbscan_silhouette,
        'optics_ch': calinski_harabasz_optics,
        'hdbscan_ch': calinski_harabasz_hdbscan,
        'optics_dbi': davies_bouldin_optics,
        'hdbscan_dbi': davies_bouldin_hdbscan,
    },ignore_index=True)

df.to_csv('compare.csv')