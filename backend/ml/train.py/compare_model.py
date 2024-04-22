import numpy as np
import pandas as pd
import sklearn
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import xgboost as xgb
import lightgbm as lgb
import catboost as cb
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor

# X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
df = df = pd.read_csv('total_posix_sanitize.csv', delimiter=',')
columns = set([
    c for c in df.columns if 'perc' in c.lower() or 'log10' in c.lower()
]).difference(["POSIX_LOG10_agg_perf_by_slowest"])
X = df[list(columns)]
y = df.POSIX_LOG10_agg_perf_by_slowest

xgbs = []
lgbs = []
cbs = []
lrs = []
dts = []
rfs = []

for i in range(100):
    X_train, X_test, y_train, y_test = sklearn.model_selection.train_test_split(
        X, y, test_size=0.2)

    # 训练 XGBoost 模型
    xgb_model = xgb.XGBRegressor()
    xgb_model.fit(X_train, y_train)
    y_pred_xgb = xgb_model.predict(X_test)
    rmse_xgb = np.sqrt(mean_squared_error(y_test, y_pred_xgb))

    # 训练 LightGBM 模型
    lgb_model = lgb.LGBMRegressor()
    lgb_model.fit(X_train, y_train)
    y_pred_lgb = lgb_model.predict(X_test)
    rmse_lgb = np.sqrt(mean_squared_error(y_test, y_pred_lgb))

    # 训练 CatBoost 模型
    cb_model = cb.CatBoostRegressor(verbose=0)
    cb_model.fit(X_train, y_train)
    y_pred_cb = cb_model.predict(X_test)
    rmse_cb = np.sqrt(mean_squared_error(y_test, y_pred_cb))

    # # 线性回归模型
    # lr_model = LinearRegression()
    # lr_model.fit(X_train, y_train)
    # y_pred_lr = lr_model.predict(X_test)
    # rmse_lr = np.sqrt(mean_squared_error(y_test, y_pred_lr))
    # lrs.append(rmse_lr)

    # 决策树模型
    dt_model = DecisionTreeRegressor()
    dt_model.fit(X_train, y_train)
    y_pred_dt = dt_model.predict(X_test)
    rmse_dt = np.sqrt(mean_squared_error(y_test, y_pred_dt))
    dts.append(rmse_dt)

    # 随机森林模型
    rf_model = RandomForestRegressor()
    rf_model.fit(X_train, y_train)
    y_pred_rf = rf_model.predict(X_test)
    rmse_rf = np.sqrt(mean_squared_error(y_test, y_pred_rf))
    rfs.append(rmse_rf)

    xgbs.append(rmse_xgb)
    lgbs.append(rmse_lgb)
    cbs.append(rmse_cb)

# # 绘制箱型图比较
plt.figure(figsize=(8, 6))
plt.title('RMSE Comparison')
plt.ylabel('RMSE')

df = pd.DataFrame.from_dict({
    "Error":
    np.concatenate([xgbs, lgbs, cbs,  dts, rfs]),
    "Classifier": ["XGBoost"] * len(xgbs) + ["LightGBM"] * len(lgbs) +
    ["CatBoost"] * len(cbs) + 
    ['DecisionTree'] * len(dts) + ['RandomForest'] * len(rfs)
})
#
# Plotting error boxplots
#
sns.boxplot(data=df, y="Error", x="Classifier", palette="Set2")

plt.savefig('models.jpg')