'''
Author       : Outsider
Date         : 2023-12-08 17:36:41
LastEditors  : Outsider
LastEditTime : 2023-12-18 19:41:16
Description  : In User Settings Edit
FilePath     : /thesis/backend/dp/dataset.py
'''
import pandas as pd
import glob


def Get_dataset(path):
    df = pd.read_csv(path, delimiter='|')

    return df


if __name__ == "__main__":
    df = Get_dataset("data/anon.csv")
    print(df.columns)
    print(df)