#%%
''''
Bias Correction of daily precipitation climate projections 
using Quantile Delta Mapping, 
accounting for observed seasonality

'''
__author__ = "Carlos Eduardo Sousa Lima"
__license__ = "GPL"
__version__ = "2.0"
__email__ = "carlosesl07@gmail.com"
__maintainer__ = "Carlos Eduardo Sousa Lima"
__status__ = "Production"



import pandas as pd
import numpy as np
from glob import glob
import scipy.stats as st

#%%
def cdf_inflated_zero(x, fitted_args_non_zero, p_zero):
    x = np.atleast_1d(x)

    cdf = np.zeros_like(x, dtype=float)
    
    cdf[x == 0] = p_zero
    
    mask_pos = x > 0

    cdf[mask_pos] = p_zero + (1 - p_zero) * st.gamma.cdf(x[mask_pos], *fitted_args_non_zero)
    
    return cdf

def ppf_inflated_zero(q, fitted_args_non_zero, p_zero):
    q = np.atleast_1d(q)
    if np.any((q < 0) | (q > 1)):
        raise ValueError("Probabilidades fora dos limites (0 a 1)")
    
    x = np.zeros_like(q, dtype=float)
    
    # Valores onde q <= p_zero já ficam com 0 (comportamento padrão do np.zeros_like)
    mask_pos = q > p_zero
    
    # Calcula apenas para valores maiores que p_zero
    q_adj = (q[mask_pos] - p_zero) / (1 - p_zero)
    x[mask_pos] = st.gamma.ppf(q_adj, *fitted_args_non_zero)
    return x

def get_p_zero(x):

    return np.sum(x == 0)/len(x)

#%%
df_obs = pd.read_parquet("daily_obs.pqt")
list_models = glob("raw_daily/*.pqt")

list_hist = [x for x in list_models if "historical" in x]

for path_hist in list_hist:

    df_hist = pd.read_parquet(path_hist)

    model = path_hist.split("\\")[-1].split("_")[2]


    for sc in ["ssp245", "ssp585"]:
        path_sc = path_hist.replace("historical", sc)

        df_fcst = pd.read_parquet(path_sc)

        df_adj = pd.DataFrame(np.nan,
            index = df_fcst.index,
            columns = ["pr"]
        )

        for mon in range(1,13,1):

            sel_obs = df_obs.loc[df_obs.index.month == mon]

            sel_hist = df_hist.loc[df_hist.index.month == mon]
            sel_fcst = df_fcst.loc[df_fcst.index.month == mon]


            x_obs = sel_obs.dropna().to_numpy().flatten()
            x_hist = sel_hist.dropna().to_numpy().flatten()
            x_fcst = sel_fcst.dropna().to_numpy().flatten()


            p_zero_obs = get_p_zero(x_obs)
            p_zero_hist = get_p_zero(x_hist)
            p_zero_fcst = get_p_zero(x_fcst)

            args_obs = st.gamma.fit(x_obs[x_obs>0], floc = 0)

            args_hist = st.gamma.fit(x_hist[x_hist>0], floc = 0)

            args_fcst = st.gamma.fit(x_fcst[x_fcst>0], floc = 0)

            x_fcst_adj = np.zeros_like(x_fcst, dtype = "float")

            p_fcst = cdf_inflated_zero(x_fcst, args_fcst, p_zero_fcst)

            hist_eq = ppf_inflated_zero(p_fcst, args_hist, p_zero_hist)

            obs_eq = ppf_inflated_zero(p_fcst, args_obs, p_zero_obs)

            mask_nonzero = hist_eq > 0

            x_fcst_adj[mask_nonzero] = obs_eq[mask_nonzero] + (x_fcst[mask_nonzero]/hist_eq[mask_nonzero])

            #fallback para correcao aditiva
            #hist_eq == 0 nao permite a correcao multiplicativa
            mask_zero = (hist_eq == 0) & (x_fcst > 0)

            x_fcst_adj[mask_zero] = obs_eq[mask_zero] + x_fcst[mask_zero]

            
            df_adj.loc[sel_fcst.index, "pr"] = x_fcst_adj

            df_adj.to_parquet("adj_daily/{}".format(path_sc.split("\\")[-1]))
#%%
