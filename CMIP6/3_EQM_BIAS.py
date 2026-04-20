#%%
__author__ = "Carlos Eduardo Sousa Lima"
__license__ = "GPL"
__version__ = "2.0"
__email__ = "carlosesl07@gmail.com"
__maintainer__ = "Carlos Eduardo Sousa Lima"
__status__ = "Production"

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as st
from glob import glob

#%%

amp_obs = pd.read_pickle("AMP_obs.pkl")

amp_obs.dropna(inplace = True)
amp_obs = amp_obs.sort_index()
params_obs = st.gumbel_r.fit(amp_obs, method = "MLE")

list_csv = glob("raw_AMP/*.pkl")

list_hist = [x for x in list_csv if "historical" in x]

scenarios = ["ssp245", "ssp585"]

df_100 = pd.DataFrame(columns = scenarios)
df_1000 = pd.DataFrame(columns = scenarios)
df_10000 = pd.DataFrame(columns = scenarios)

pr_100 = st.gumbel_r.ppf(1-(1/100), *params_obs)
pr_1000 = st.gumbel_r.ppf(1-(1/1000), *params_obs)
pr_10000 = st.gumbel_r.ppf(1-(1/10000), *params_obs)
#%%
for path_hist in list_hist:

    df_hist = pd.read_pickle(path_hist)
    amp_hist = df_hist.resample("YS").max()
    amp_hist = amp_hist.loc[
        (amp_hist.index.year >= amp_obs.index[0]) & 
        (amp_hist.index.year <= amp_obs.index[-1])]
    
    params_hist = st.gumbel_r.fit(amp_hist, method = "MLE")
    model = path_hist.split("\\")[-1].split("_")[3]

    for sc in scenarios:
        path_fcst = [x for x in list_csv if model in x]
        path_fcst = [x for x in path_fcst if sc in x]
        
        df_fcst = pd.read_pickle(path_fcst[0])
        amp_fcst = df_fcst.resample("YS").max()
        amp_fcst = amp_fcst.loc[amp_fcst.index.year >= 2026]

        amp_fcst = df_fcst.resample("YS").max()
        amp_fcst = amp_fcst.loc[amp_fcst.index.year >= 2026]

    
    
        params_fcst = st.gumbel_r.fit(amp_fcst, method = "MLE")

        adj_list = []

        for x in amp_fcst.values:
        
            prob_fcst = st.gumbel_r.cdf(x, *params_fcst)

            adj1 = st.gumbel_r.ppf(prob_fcst, *params_obs)
            adj2 = st.gumbel_r.ppf(prob_fcst, *params_hist)

            x_adj = x + adj1 - adj2

            adj_list.append(x_adj)

        amp_fcst_adj = pd.DataFrame(adj_list, index = amp_fcst.index)

        amp_fcst_adj.to_pickle("adj_AMP/AMP_{}_{}.pkl".format(model, sc))

        params_adj = st.gumbel_r.fit(amp_fcst_adj, method = "MLE")

        df_100.loc[model, sc] = st.gumbel_r.ppf(1-(1/100), *params_adj)
        df_1000.loc[model, sc] = st.gumbel_r.ppf(1-(1/1000), *params_adj)
        df_10000.loc[model, sc] = st.gumbel_r.ppf(1-(1/10000), *params_adj)
        
#%%
for df, pr, tr in zip([df_100, df_1000, df_10000], [pr_100, pr_1000, pr_10000], ["Tr - 100", "Tr - 1.000", "Tr - 10.000"]):
    fig, ax = plt.subplots(dpi = 600)
    ax.boxplot(df)
    ax.axhline(pr, label = "Observada", c = "red")
    ax.set_title(tr, loc = "left")
    ax.legend()
    ax.set_ylabel("Precipitação (mm)")
    # fig.savefig("{}.png".format(tr), dpi = 600, bbox_inches = "tight", facecolor = 'w')




# %%
