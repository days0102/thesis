from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score
from sklearn.cluster import AgglomerativeClustering
from sklearn.cluster import OPTICS
import hdbscan
from sklearn.datasets import make_blobs
import pandas as pd
import itertools

# 生成示例数据
df = df = pd.read_csv('posix_sanitize.csv', delimiter=',')
columns = set([
    c for c in df.columns if 'perc' in c.lower() or 'log10' in c.lower()
]).difference(["POSIX_LOG10_agg_perf_by_slowest"])
X = df[list(columns)]

# 聚类算法的参数设置
agglomerative = AgglomerativeClustering(n_clusters=10)
optics = OPTICS(min_samples=50, xi=0.05, min_cluster_size=0.1)
hdbscan_clusterer = hdbscan.HDBSCAN(min_samples=10)

# 聚类
agglomerative_labels = agglomerative.fit_predict(X)
optics_labels = optics.fit_predict(X)
hdbscan_labels = hdbscan_clusterer.fit_predict(X)

print(agglomerative.children_)

ii = itertools.count(X.shape[0])
print([{'node_id': next(ii), 'left': x[0], 'right':x[1]} for x in agglomerative.children_])

# 使用评价指标进行比较
silhouette_agglomerative = silhouette_score(X, agglomerative_labels)
silhouette_optics = silhouette_score(X, optics_labels)
silhouette_hdbscan = silhouette_score(X, hdbscan_labels)

calinski_harabasz_agglomerative = calinski_harabasz_score(
    X, agglomerative_labels)
calinski_harabasz_optics = calinski_harabasz_score(X, optics_labels)
calinski_harabasz_hdbscan = calinski_harabasz_score(X, hdbscan_labels)

davies_bouldin_agglomerative = davies_bouldin_score(X, agglomerative_labels)
davies_bouldin_optics = davies_bouldin_score(X, optics_labels)
davies_bouldin_hdbscan = davies_bouldin_score(X, hdbscan_labels)

print("Silhouette Score:")
print("Agglomerative Clustering:", silhouette_agglomerative)
print("OPTICS:", silhouette_optics)
print("HDBSCAN:", silhouette_hdbscan)
print()
print("Calinski-Harabasz Score:")
print("Agglomerative Clustering:", calinski_harabasz_agglomerative)
print("OPTICS:", calinski_harabasz_optics)
print("HDBSCAN:", calinski_harabasz_hdbscan)
print()
print("Davies-Bouldin Score:")
print("Agglomerative Clustering:", davies_bouldin_agglomerative)
print("OPTICS:", davies_bouldin_optics)
print("HDBSCAN:", davies_bouldin_hdbscan)
