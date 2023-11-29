import pandas as pd

def load_data(path:str):

    df=pd.read_csv(path, delimiter='|')

    pass

if __name__=="__main__":
    load_data("../data")