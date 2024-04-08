from ml import cluster
import networkx as nx

import sklearn
import xgboost as xgb
import numpy as np
import pandas as pd
import shap

import matplotlib.pyplot as plt, mpld3

df, clusterer = cluster.init()
G = clusterer.condensed_tree_.to_networkx()


def get_leaves(G):
    return {
        x
        for x in G.nodes() if G.out_degree(x) == 0 and G.in_degree(x) == 1
    }


def train(X, y, feature_num):
    """
    Splits the dataset into a training and test set, and trains an XGBoost model.
    Plots the test set errors in a box plot.
    Optionally plots a SHAP summary plot.
    """
    def huber_approx_obj(y_pred, y_test):
        """
        Huber loss, adapted from https://stackoverflow.com/questions/45006341/xgboost-how-to-use-mae-as-objective-function
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
    xgb_model = xgb.XGBRegressor(obj=huber_approx_obj)
    lin_model = sklearn.linear_model.SGDRegressor(loss='huber')
    dmy_model = sklearn.dummy.DummyRegressor(strategy="median")
    xgb_model.fit(X_train, y_train, eval_metric=huber_approx_obj)
    lin_model.fit(X_train, y_train)
    dmy_model.fit(X_train, y_train)

    xgb_error = 10**np.abs(y_test - xgb_model.predict(X_test))
    lin_error = 10**np.abs(y_test - lin_model.predict(X_test))
    dmy_error = 10**np.abs(y_test - dmy_model.predict(X_test))

    #
    # Plotting SHAP summary plot
    #
    explainer = shap.TreeExplainer(xgb_model, shap.sample(X_train, 100))
    shap_values = explainer.shap_values(X)
    # feature_names = list(map(feature_name_mapping.mapping.get, X.columns))
    # fig = plt.figure()
    # sd = shap.summary_plot(shap_values,
    #                        X,
    #                     #    X.columns,
    #                        show=False,
    #                        max_display=8,
    #                        color_bar=False)
    # plt.savefig('shap.jpg')
                        

    # for pos, i in enumerate(feature_order):
    #     shaps = shap_values[:, i]
    #     # values = None if X is None else X[:, i]
    #     inds = np.arange(len(shaps))
    #     np.random.shuffle(inds)
    #     shaps = shaps[inds]

    feature_order = np.argsort(np.sum(np.abs(shap_values), axis=0))
    # print(feature_order)
    feature_order = feature_order[-min(8, len(feature_order)):]
    print(feature_order)

    print(shap_values[:, feature_order],X.columns[feature_order])
    df = pd.DataFrame(shap_values[:, feature_order],
                      columns=X.columns[feature_order])
    print(df)

    if isinstance(shap_values, list):
        print('list')

    return df

    # axes = fig.get_axes()
    # data=[]
    # print(axes[0].dataLim)
    # for line in axes[0].get_lines():
    #     line_data = {
    #         'x_data': line.get_xdata(),
    #         'y_data': line.get_ydata()
    #     }
    #     data.append(line_data)
    # print(data)

    # xticklabels = axes[0].get_yticklabels()
    # feature_names_from_plot = [label.get_text() for label in xticklabels]
    # print("Feature names from plot:", feature_names_from_plot)
    # pt=shap.force_plot(explainer.expected_value, shap_values[0,:], X.iloc[0,:])
    # shap.save_html('shap.html',pt)

    # df = pd.DataFrame.from_dict({
    #     "Error":
    #     np.concatenate([dmy_error, lin_error, xgb_error]),
    #     "Classifier": ["Constant"] * len(dmy_error) +
    #     ["Linear"] * len(lin_error) + ["XGB"] * len(xgb_error),
    # })

    # print(X_test.shape)
    # print(shap_values.shape)
    # print(shap_values)

    # print(shap_values.feature_names)
    # # X_test['shape_values'] = shap_values
    # most_important_features = list(
    #     reversed(X.columns[np.argsort(
    #         np.abs(shap_values).mean(0))]))[:feature_num]
    # print(most_important_features)

    # return X_test

    #
    # Plotting correlation matrix between most important features according to SHAP and any high-corr. features
    #

    return mpld3.fig_to_html(
        fig,
        d3_url="../assets/d3.v7.js",
        mpld3_url="../assets/mpld3.js",
    )


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
    print(clusters)
    print(input_columns)
    print(df.iloc[list(clusters)][input_columns].shape)

    print('--------------')

    return train(df.iloc[list(clusters)][input_columns],
                 df.iloc[list(clusters)].POSIX_LOG10_agg_perf_by_slowest, 5)


if __name__ == "__main__":
    df, clusterer = cluster.init()
    G = clusterer.condensed_tree_.to_networkx()
    print(clusterer.condensed_tree_.to_pandas().head())
    top_clusters = [get_leaves(nx.dfs_tree(G, c)) for c in [3464]]
    print(top_clusters)