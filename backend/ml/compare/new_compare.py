from sklearn.cluster import Birch, OPTICS
import hdbscan
from sklearn.datasets import make_blobs
from sklearn.metrics import adjusted_rand_score, silhouette_score
import pandas as pd

# 生成示例数据
df = df = pd.read_csv('posix_sanitize.csv', delimiter=',')
columns = set([
    c for c in df.columns if 'perc' in c.lower() or 'log10' in c.lower()
]).difference(["POSIX_LOG10_agg_perf_by_slowest"])
X = df[list(columns)]

# 初始化Birch算法
birch = Birch(n_clusters=None, threshold=0.5)
birch_labels = birch.fit_predict(X)

# 初始化OPTICS算法
optics = OPTICS(min_samples=10)
optics_labels = optics.fit_predict(X)
print(optics.cluster_hierarchy_)

# 初始化HDBSCAN算法
hdbscan_labels = hdbscan.HDBSCAN(min_cluster_size=10).fit_predict(X)


birch_silhouette = silhouette_score(X, birch_labels)
optics_silhouette = silhouette_score(X, optics_labels)
hdbscan_silhouette = silhouette_score(X, hdbscan_labels)

print("Birch Silhouette Score:", birch_silhouette)
print("OPTICS Silhouette Score:", optics_silhouette)
print("HDBSCAN Silhouette Score:", hdbscan_silhouette)
