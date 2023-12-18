'''
Author       : Outsider
Date         : 2023-11-29 14:18:49
LastEditors  : Outsider
LastEditTime : 2023-12-18 21:13:05
Description  : In User Settings Edit
FilePath     : /thesis/backend/ml/hdb.py
'''
import pandas as pd
import hdbscan


def load_data(path: str):
    df = pd.read_csv(path, delimiter='|')
    return df


if __name__ == "__main__":
    df = load_data("data/anon.csv")
    print(df)

    columns = set([
        c for c in df.columns if 'perc' in c.lower() or 'log10' in c.lower()
    ]).difference(["POSIX_LOG10_agg_perf_by_slowest"])
    hdbs = hdbscan.HDBSCAN(min_samples=10,
                           cluster_selection_epsilon=5,
                           metric='manhattan',
                           gen_min_span_tree=True)
    cluster = hdbs.fit(df[list(columns)])

    print(cluster)