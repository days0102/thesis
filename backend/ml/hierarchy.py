def build_hierarchy(df, clusterer):
    ct = clusterer.condensed_tree_
    G = ct.to_networkx()
