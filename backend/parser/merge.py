import pandas as pd

if __name__ == '__main__':
    km_vi = pd.read_csv('out/km_vi.csv')
    print(km_vi)
    km_sil = pd.read_csv('out/km_sil.csv')
    print(km_sil)
    km_dbi = pd.read_csv('out/km_dbi.csv')
    print(km_dbi)
    km_ch = pd.read_csv('out/km_ch.csv')
    print(km_ch)

    col = [['clusters', 'vi'], ['clusters', 'silhouette'], ['clusters', 'dbi'],
           ['clusters', 'ch']]
    res_km = pd.concat(
        [km_vi[col[0]], km_sil['silhouette'], km_dbi['dbi'], km_ch['ch']],
        axis=1)

    print(res_km)

    res_km.to_csv('out/km_tol.csv')

    # =+++++++++++++++++++++++

    dbs_vi = pd.read_csv('out/dbs_vi.csv')
    print(dbs_vi)
    dbs_sil = pd.read_csv('out/dbs_sil.csv')
    print(dbs_sil)
    dbs_dbi = pd.read_csv('out/dbs_dbi.csv')
    print(dbs_dbi)
    dbs_ch = pd.read_csv('out/dbs_ch.csv')
    print(dbs_ch)

    col = [['clusters', 'vi'], ['clusters', 'silhouette'], ['clusters', 'dbi'],
           ['clusters', 'ch']]
    res_dbs = pd.concat(
        [dbs_vi[col[0]], dbs_sil['silhouette'], dbs_dbi['dbi'], dbs_ch['ch']],
        axis=1)

    print(res_dbs)

    res_dbs.to_csv('out/dbs_tol.csv')

    # =+++++++++++++++++++++++
    gmm_vi = pd.read_csv('out/gmm_vi.csv')
    print(gmm_vi)
    gmm_sil = pd.read_csv('out/gmm_sil.csv')
    print(gmm_sil)
    gmm_dbi = pd.read_csv('out/gmm_dbi.csv')
    print(km_dbi)
    gmm_ch = pd.read_csv('out/gmm_ch.csv')
    print(gmm_ch)

    col = [['clusters', 'vi'], ['clusters', 'silhouette'], ['clusters', 'dbi'],
           ['clusters', 'ch']]
    res_gmm = pd.concat(
        [gmm_vi[col[0]], gmm_sil['silhouette'], gmm_dbi['dbi'], gmm_ch['ch']],
        axis=1)

    print(res_gmm)

    res_gmm.to_csv('out/gmm_tol.csv')

    # =++++++++++++++++++++
    msc_vi = pd.read_csv('out/msc_vi.csv')
    print(msc_vi)
    msc_sil = pd.read_csv('out/msc_sil.csv')
    print(msc_sil)
    msc_dbi = pd.read_csv('out/msc_dbi.csv')
    print(msc_dbi)
    msc_ch = pd.read_csv('out/msc_ch.csv')
    print(msc_ch)

    col = [['clusters', 'vi'], ['clusters', 'silhouette'], ['clusters', 'dbi'],
           ['clusters', 'ch']]
    res_msc = pd.concat(
        [msc_vi[col[0]], msc_sil['silhouette'], msc_dbi['dbi'], msc_ch['ch']],
        axis=1)

    print(res_msc)

    res_msc.to_csv('out/msc_tol.csv')

    res_vi = pd.concat([
        res_dbs[['clusters', 'vi']], res_km['vi'], res_gmm['vi'], res_msc['vi']
    ],
                       axis=1)
    res_vi.columns = ['clusters', 'dbs_vi', 'km_vi', 'gmm_vi', 'msc_vi']
    print(res_vi)

    res_vi.to_csv('out/vi_tol.csv')

    #=++++++++++++++++++

    res_dbi = pd.concat([
        res_dbs[['clusters', 'dbi']], res_km['dbi'], res_gmm['dbi'],
        res_msc['dbi']
    ],
                        axis=1)
    res_dbi.columns = ['clusters', 'dbs_dbi', 'km_dbi', 'gmm_dbi', 'msc_dbi']
    print(res_dbi)

    res_dbi.to_csv('out/dbi_tol.csv')

    #=++++++++++++++++++

    res_ch = pd.concat([
        res_dbs[['clusters', 'ch']], res_km['ch'], res_gmm['ch'], res_msc['ch']
    ],
                       axis=1)
    res_ch.columns = ['clusters', 'dbs_ch', 'km_ch', 'gmm_ch', 'msc_ch']
    print(res_ch)

    res_dbi.to_csv('out/dbi_tol.csv')

    #=++++++++++++++++++

    res_sil = pd.concat([
        res_dbs[['clusters', 'silhouette']], res_km['silhouette'],
        res_gmm['silhouette'], res_msc['silhouette']
    ],
                        axis=1)
    res_sil.columns = [
        'clusters', 'dbs_silhouette', 'km_silhouette', 'gmm_silhouette',
        'msc_silhouette'
    ]
    print(res_sil)

    res_sil.to_csv('out/sil_tol.csv')