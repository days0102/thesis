from ml import cluster
import networkx as nx

import sklearn
import xgboost as xgb
import numpy as np
import pandas as pd
import shap

import catboost as cb

import matplotlib.pyplot as plt

import io
import base64

df, clusterer = cluster.init()
G = clusterer.condensed_tree_.to_networkx()
explainers = {}


def get_leaves(G):
    # 获取叶节点（所有的作业id）
    return {
        x
        for x in G.nodes() if G.out_degree(x) == 0 and G.in_degree(x) == 1
    }


def train(X, y, cluster_id, feature_num):
    """
    训练预测模型 CatBoost
    """
    def huber_approx_obj(y_pred, y_test):
        """
        Huber loss, https://stackoverflow.com/questions/45006341/xgboost-how-to-use-mae-as-objective-function
        """
        d = y_pred - y_test
        h = 5  # h is delta in the graphic
        scale = 1 + (d / h)**2
        scale_sqrt = np.sqrt(scale)
        grad = d / scale_sqrt
        hess = 1 / scale / scale_sqrt
        return grad, hess

    X_train, X_test, y_train, y_test = sklearn.model_selection.train_test_split(
        X, y, test_size=0.2)
    # xgb_model = xgb.XGBRegressor(obj=huber_approx_obj)
    cb_model = cb.CatBoostRegressor(verbose=0)# verbose=0不打印训练过程信息
    # lin_model = sklearn.linear_model.SGDRegressor(loss='huber')
    # dmy_model = sklearn.dummy.DummyRegressor(strategy="median")
    # xgb_model.fit(X, y, eval_metric=huber_approx_obj)
    cb_model.fit(X, y)
    # lin_model.fit(X, y)
    # dmy_model.fit(X, y)

    # xgb_error = 10**np.abs(y_test - xgb_model.predict(X_test))
    # lin_error = 10**np.abs(y_test - lin_model.predict(X_test))
    # dmy_error = 10**np.abs(y_test - dmy_model.predict(X_test))

    # SHAP summary plot
    # explainer = shap.TreeExplainer(xgb_model)
    explainer = shap.TreeExplainer(cb_model) #模型解释
    explainers[cluster_id] = explainer  # 存储解释器
    # explainer = shap.TreeExplainer(xgb_model, shap.sample(X_train, 100))
    shap_values = explainer.shap_values(X)
    # feature_names = list(map(feature_name_mapping.mapping.get, X.columns))
    # fig = plt.figure()
    # shap.plots.bar(explainer(X)[1], show_data=True)
    # plt.savefig('local_shap.jpg')
    # shap.force_plot(explainer.expected_value,
    #                 shap_values[0, :],
    #                 X.iloc[0, :],
    #                 matplotlib=True,
    #                 show=False)
    # plt.savefig('force_shap.jpg')

    feature_order = np.argsort(np.sum(np.abs(shap_values), axis=0))
    # print(feature_order)
    feature_order = feature_order[-min(8, len(feature_order)):]
    # print(feature_order)
    # print(X.columns[feature_order])

    # print(shap_values[:, feature_order], X.columns[feature_order])
    df = pd.DataFrame(shap_values[:, feature_order],
                      columns=X.columns[feature_order])

    df_data = pd.DataFrame(X.iloc[:, feature_order],
                           columns=X.columns[feature_order])

    # print(df_data.iat[33,0])
    return df, df_data


def fetch_force_plot(cluster_id, index):
    if explainers[cluster_id] is None:
        return
    X, y = build_X_y(cluster_id)
    shap_values = explainers[cluster_id].shap_values(X)
    # print(np.round(shap_values[index, :], decimals=3))
    # fig=plt.figure()
    shap.force_plot(explainers[cluster_id].expected_value,
                    shap_values[index, :],
                    np.round(X.iloc[index, :], decimals=3),
                    matplotlib=True,
                    show=False,
                    text_rotation=20)
    w, h = plt.gcf().get_size_inches()
    plt.gcf().set_size_inches(w, 1.5 * h)
    plt.xticks(rotation=25)  # 设置x轴标签旋转角度
    plt.tight_layout(pad=2)

    # 将图片保存到内存中
    img_data = io.BytesIO()
    plt.savefig(img_data, format='png')
    img_data.seek(0)

    # 将图片数据转换为 base64 字符串
    base64_img = base64.b64encode(img_data.getvalue()).decode()
    return base64_img


def fetch_bar_plot(cluster_id, index):
    if explainers[cluster_id] is None:
        return
    X, y = build_X_y(cluster_id)
    shap_values = explainers[cluster_id](X)
    fig = plt.figure()
    # print(explainer(X))
    shap.plots.bar(shap_values[index], show_data=True, show=False)
    # plt.yticks(rotation=25)    # 设置x轴标签旋转角度
    plt.tick_params(axis='y', direction='out', pad=20)
    plt.tight_layout(pad=2)
    # plt.title('Local Feature Importance')
    # _, h = plt.gcf().get_size_inches()
    # plt.gcf().set_size_inches(h*5, h)

    # 将图片保存到内存中
    img_data = io.BytesIO()
    plt.savefig(img_data, format='png')
    img_data.seek(0)

    # 将图片数据转换为 base64 字符串
    base64_img = base64.b64encode(img_data.getvalue()).decode()
    return base64_img


def all_leaves(cluster_id):
    return get_leaves(nx.dfs_tree(G, cluster_id))


def build_X_y(cluster_id):
    clusters = get_leaves(nx.dfs_tree(G, cluster_id))
    input_columns = list(
        set([c for c in df.columns
             if 'perc' in c.lower() or 'LOG10' in c]).difference([
                 "POSIX_LOG10_agg_perf_by_slowest", "LOG10_runtime",
                 "POSIX_LOG10_SEEKS", "POSIX_LOG10_MODE", "POSIX_LOG10_STATS",
                 'POSIX_ACCESS1_COUNT_PERC', 'POSIX_ACCESS2_COUNT_PERC',
                 'POSIX_ACCESS3_COUNT_PERC', 'POSIX_ACCESS4_COUNT_PERC'
             ]))
    return df.iloc[list(clusters)][input_columns], df.iloc[list(
        clusters)].POSIX_LOG10_agg_perf_by_slowest


def fetch_clusters(cluster_id):
    clusters = get_leaves(nx.dfs_tree(G, cluster_id))

    input_columns = list(
        set([c for c in df.columns
             if 'perc' in c.lower() or 'LOG10' in c]).difference([
                 "POSIX_LOG10_agg_perf_by_slowest", "LOG10_runtime",
                 "POSIX_LOG10_SEEKS", "POSIX_LOG10_MODE", "POSIX_LOG10_STATS",
                 'POSIX_ACCESS1_COUNT_PERC', 'POSIX_ACCESS2_COUNT_PERC',
                 'POSIX_ACCESS3_COUNT_PERC', 'POSIX_ACCESS4_COUNT_PERC'
             ]))
    # print(clusters)
    # print(input_columns)
    # print(df.iloc[list(clusters)][input_columns].shape)

    # print('--------------')
    shap_values, df_data = train(
        df.iloc[list(clusters)][input_columns],
        df.iloc[list(clusters)].POSIX_LOG10_agg_perf_by_slowest, cluster_id, 5)

    return shap_values, df_data


if __name__ == "__main__":
    df, clusterer = cluster.init()
    G = clusterer.condensed_tree_.to_networkx()
    print(clusterer.condensed_tree_.to_pandas().head())
    top_clusters = [get_leaves(nx.dfs_tree(G, c)) for c in [3464]]
    print(top_clusters)