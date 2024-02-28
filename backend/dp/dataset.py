'''
Author       : Outsider
Date         : 2023-12-08 17:36:41
LastEditors  : Outsider
LastEditTime : 2023-12-18 19:41:16
Description  : In User Settings Edit
FilePath     : /thesis/backend/dp/dataset.py
'''
import pandas as pd
import numpy as np
import glob


def Get_dataset(path):
    df = pd.read_csv(path, delimiter=',')

    return df


def remove_invalid_feature(df, min_drop_prec=0.5):
    drop_columns = []
    for idx, c in enumerate(df.columns):
        print(idx, c)
        if df.dtypes.iloc[idx] == np.int64 or df.dtypes.iloc[idx] == np.float64:
            print(df[c])
            tol = np.sum(df[c] < 0)
            print(tol)

            if df.shape[1] * min_drop_prec < tol:
                drop_columns.append(c)


def sanitize(df):

    remove_invalid_feature(df, 0.5)


if __name__ == "__main__":
    # df = Get_dataset("data/anon.csv")
    df = Get_dataset("posix.csv")
    print(df.columns)
    print(df)
    sanitize(df)