
import sklearn
import xgboost as xgb
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt

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

if __name__=='__main__':
    # 生成示例数据
    df = df = pd.read_csv('posix_sanitize.csv', delimiter=',')
    columns = set([
        c for c in df.columns if 'perc' in c.lower() or 'log10' in c.lower()
    ]).difference(["POSIX_LOG10_agg_perf_by_slowest"])
    X = df[list(columns)]
    y= df.POSIX_LOG10_agg_perf_by_slowest

    X_train, X_test, y_train, y_test = sklearn.model_selection.train_test_split(
        X, y, test_size=0.2)
    xgb_model = xgb.XGBRegressor(eval_metric='rmse')
    xgb_model.fit(X, y)

    xgb_error = 10**np.abs(y_test - xgb_model.predict(X_test))

    print(xgb_error)