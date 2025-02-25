import glob
import os
import numpy as np
import sys
import pandas as pd
import hdbscan
import networkx as nx
from networkx.readwrite import json_graph


def load_dataset(path):
    df = pd.read_csv(path, delimiter=',')
    df = df.reset_index()
    return df


def train_ml(path=None):

    df = load_dataset(path)

    # Build the clusterer
    train_columns = [
        c for c in df.columns if 'perc' in c.lower() or 'log10' in c.lower()
    ]
    clusterer = hdbscan.HDBSCAN(min_samples=10,
                                cluster_selection_epsilon=5,
                                metric='manhattan',
                                gen_min_span_tree=True)
    clusterer.fit(df[train_columns])

    return df, clusterer


def calc_node_size(G, node):
    children = list(G[node])
    if len(children) == 0:
        size = 1
    else:
        size = sum(
            [calc_node_size(G, children[c]) for c in range(len(children))])

    G.nodes[node]['size'] = size

    return size


def populate_users_and_apps(df, G, node):
    children = list(G[node])
    if len(children) == 0:
        apps = set([df.iloc[node]['exe']])
        users = set([int(df.iloc[node]['uid'])])
    else:
        apps, users = set(), set()
        for c in range(len(children)):
            a, u = populate_users_and_apps(df, G, children[c])
            apps = apps.union(a)
            users = users.union(u)

    G.nodes[node]['apps'] = apps
    G.nodes[node]['users'] = users

    return apps, users


def merge_chain_nodes(G, node, dont_merge=[]):
    """
    Traverses the graph, and converts chains such as A-B-C to A-C or A-B to B.
    Dont merge specifies nodes that should not be merged even if part of chain
    """
    if len(list(G.predecessors(node))) == 1 and len(list(
            G.successors(node))) == 1 and node not in dont_merge:
        parent = list(G.predecessors(node))[0]
        child = list(G.successors(node))[0]  # noqa: E211
        weight = G[node][child]['weight']

        # G.remove_edges_from([(parent, node), (node, child)])
        G.remove_node(node)
        G.add_weighted_edges_from([(parent, child, weight)])

        merge_chain_nodes(G, child)
    else:
        for child in list(G.successors(node)):
            merge_chain_nodes(G, child)


def build_condensed_graph(G, min_epsilon, min_cluster_size, dont_merge=[]):
    """ 
    Finds nodes in the graph that have edges weight weights above min_epsilon,
    and both children have a size larger than min_cluster_size.
    """
    def filter_node(n):
        return G.nodes[n]['size'] > min_cluster_size

    def filter_edge(n1, n2):
        return 1 / G[n1][n2]['weight'] > min_epsilon

    SG = nx.subgraph_view(G, filter_node=filter_node, filter_edge=filter_edge)
    SG = nx.DiGraph(SG)

    root = [n for n, d in SG.in_degree() if d == 0][0]
    merge_chain_nodes(SG, root, dont_merge=dont_merge)

    # Remove orphans
    SG.remove_nodes_from(list(nx.isolates(SG)))

    return SG


def tree_layout(G, min_yaxis_spacing=0.5, layout_type='middle'):
    def dfs_assignment(G, node, pos, next_x, min_yaxis_spacing):
        """
        递归计算节点的位置
        node: 节点id
        pos: {node_id:[x,y]}
        Calculates the node's position and recursively calculates it's childrens positions.
        The y position is calculated from epsilon, while the x position is calculated by first
        assigning leaves integer positions, and the branches take the average of their children.
        """
        parent = list(G.predecessors(node))
        children = list(G.successors(node))

        # Calculate X positon
        if len(children) == 0:
            x = next_x
            next_x += 1
        else:
            # Sort children by size first
            def sortby(child):
                return G.nodes[child]['size']

            children.sort(key=sortby)

            # Get children to assign their X's, and take their mean
            for child in children:
                pos, next_x = dfs_assignment(
                    G, child, pos, next_x, min_yaxis_spacing=min_yaxis_spacing)

            if layout_type == 'middle':
                x = np.mean([pos[child][0] for child in children])
            elif layout_type == 'average':
                x = np.sum([
                    pos[child][0] * G.nodes[child]['size']
                    for child in children
                ]) / np.sum([G.nodes[child]['size'] for child in children])
            else:
                raise RuntimeError(
                    "tree_layout received an unsupported layout type")

        # Calculate Y position
        if len(parent) == 1:
            y = 1 / G[parent[0]][node]['weight']
        else:
            y = 12

        pos[node] = [x, y]

        # Space out nodes on y axis
        if len(children) >= 1:
            top_child = np.max([pos[child][1] for child in children])
            if pos[node][1] - top_child < min_yaxis_spacing:
                pos[node][1] = top_child + min_yaxis_spacing

        return pos, next_x

    root = [n for n, d in G.in_degree() if d == 0][0]
    pos = {}
    pos, _ = dfs_assignment(G,
                            root,
                            pos,
                            0,
                            min_yaxis_spacing=min_yaxis_spacing)

    return pos


def print_tree_data_types(tree):
    """
    递归地打印树中所有节点的数据类型
    """
    # 打印当前节点的数据类型
    print(type(tree))

    # 如果当前节点有子节点，则递归地处理子节点
    if isinstance(tree, dict):
        for key, value in tree.items():
            print(f"Key: {key}, Type: {type(key)}")
            print_tree_data_types(value)
    elif isinstance(tree, (list, tuple)):
        for item in tree:
            print_tree_data_types(item)
    elif isinstance(tree, nx.DiGraph):
        for node in tree.nodes():
            print(f"Node: {node}, Type: {type(node)}")
            print_tree_data_types(tree.nodes[node])


def get_leaves(G):
    return [
        x for x in G.nodes() if G.out_degree(x) == 0 and G.in_degree(x) == 1
    ]


def build_cluster_to_jobs_map(clusterer, tree):
    """
    In order not to have to calculate which jobs belong to which cluster,
    we build this mapping in advance.

    Args:
        clusterer: an HDBSCAN object
        tree: a dictionary with a list of clusters 

    Returns:
        a dictionary where the key is the cluster index, and the value is 
        a list of job indexes that belong to the cluster.
    """
    G = clusterer.condensed_tree_.to_networkx()

    cluster_map = {}

    # TODO: this is hacky, we should not be iterating through a tree that is already
    # made from the clusterer
    for cluster_index in [int(c['index']) for c in tree['nodes']]:
        cluster_map[cluster_index] = get_leaves(nx.dfs_tree(G, cluster_index))

    return cluster_map


def get_cluster_jobs(df, cluster_id, cluster_map):
    return df.iloc[cluster_map[cluster_id]]


def add_averages_to_tree(df, tree, cluster_map):
    """
    For every node in the hierarchy, adds a field 'averages' which holds a map.
    The map keys are all of the features, and the values are the cluster's feature
    average.
    """

    for node in tree['nodes']:
        node['averages'] = {}
        for feature in [
                feature for feature, dtype in df.dtypes.items()
                if dtype == np.float64 or dtype == np.int64
        ]:
            node['averages'][feature] = \
                get_cluster_jobs(df,int(node['index']),cluster_map)[feature].mean()


def build_hierarchy():
    df, clusterer = train_ml('posix_sanitize.csv')

    # ref https://hdbscan.readthedocs.io/en/latest/advanced_hdbscan.html
    ct = clusterer.condensed_tree_
    G = ct.to_networkx()
    sys.setrecursionlimit(10000)

    root = [n for n, d in G.in_degree() if d == 0][0]
    calc_node_size(G, root)

    root = [n for n, d in G.in_degree() if d == 0][0]
    populate_users_and_apps(df, G, root)

    CG = build_condensed_graph(G, 0.2, min_cluster_size=10)

    coord = tree_layout(CG, layout_type='average')
    sizes = dict(nx.get_node_attributes(CG, 'size').items())

    hierarchy = {"nodes": []}
    for node in CG:
        node_object = {
            "index":
            str(node),
            "x":
            float(coord[node][0]),
            "y":
            coord[node][1],
            "epsilon":
            coord[node][1],
            "size":
            sizes[node],
            "parent":
            str(list(CG.predecessors(node))[0])
            if len(list(CG.predecessors(node))) > 0 else None,
            "children":
            list([str(x) for x in CG.successors(node)]),
            "users":
            list(CG.nodes[node]['users']),
            "apps":
            list(CG.nodes[node]['apps']),
        }

        hierarchy['nodes'].append(node_object)

    # 示例调用函数
    # print_tree_data_types(hierarchy)
    cluster_map = build_cluster_to_jobs_map(clusterer, hierarchy)
    add_averages_to_tree(df, hierarchy, cluster_map)
    return df, hierarchy, cluster_map


# for test
def init():
    df, clusterer = train_ml('posix_sanitize.csv')
    return df, clusterer


if __name__ == '__main__':
    df, clusterer = train_ml('posix_sanitize.csv')
    print(clusterer)
    print(clusterer.condensed_tree_)

    # ref https://hdbscan.readthedocs.io/en/latest/advanced_hdbscan.html
    print(clusterer.condensed_tree_.to_pandas().head())
    ct = clusterer.condensed_tree_
    G = ct.to_networkx()
    print(G)
    sys.setrecursionlimit(10000)

    root = [n for n, d in G.in_degree() if d == 0][0]
    calc_node_size(G, root)

    root = [n for n, d in G.in_degree() if d == 0][0]
    populate_users_and_apps(df, G, root)

    CG = build_condensed_graph(G, 0.1, min_cluster_size=5)

    coord = tree_layout(CG)
    sizes = dict(nx.get_node_attributes(CG, 'size').items())

    hierarchy = {"nodes": []}
    for node in CG:
        node_object = {
            "index":
            str(node),
            "x":
            float(coord[node][0]),
            "y":
            coord[node][1],
            "epsilon":
            coord[node][1],
            "size":
            sizes[node],
            "parent":
            str(list(CG.predecessors(node))[0])
            if len(list(CG.predecessors(node))) > 0 else None,
            "children":
            list([str(x) for x in CG.successors(node)]),
            "users":
            list(CG.nodes[node]['users']),
            "apps":
            list(CG.nodes[node]['apps']),
        }

        hierarchy['nodes'].append(node_object)

    print(hierarchy)