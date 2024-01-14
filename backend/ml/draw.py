import pandas as pd
import matplotlib.pyplot as plt

if __name__=='__main__':
    df = pd.read_csv('data/anon.csv', delimiter='|')
    columns = set([
        c for c in df.columns if 'perc' in c.lower() or 'log10' in c.lower()
    ]).difference(["POSIX_LOG10_agg_perf_by_slowest"])

    print(df[list(columns)])

    dbs_vi=pd.read_csv('out/dbs_vi.csv')

    print(dbs_vi)

    plt.plot(dbs_vi['clusters'],dbs_vi['vi'],label='DBSCAN',marker='*',grid=True)

    gmm_vi=pd.read_csv('out/gmm_vi.csv')

    plt.plot(gmm_vi['clusters'],gmm_vi['vi'],label='GMM')
    plt.show()

    print('Done')