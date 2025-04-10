import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def _all_positive(df):
    dfpos = pd.DataFrame(index=df.index)
    for ser, vals in list(df.items()):
        if vals.min() <= 0:
            dfpos[ser] = vals + np.abs(vals.min()) + 1
    return dfpos 

def PCA(df, variance_ratio=0.8):
    from sklearn.decomposition import PCA as sklearnPCA

    indat_pca = sklearnPCA(n_components=variance_ratio)

    indat_transf = pd.DataFrame(
        indat_pca.fit_transform(df.values), index=df.index)

    pca_colnames = ["PCA" + str(i) for i in range(indat_transf.shape[1])]
    indat_transf.columns = pca_colnames

    indat_transf_pos = _all_positive(indat_transf)

    return indat_transf_pos
