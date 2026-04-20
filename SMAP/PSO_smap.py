#%%
'''
__author__ = "Carlos Eduardo Sousa Lima"
__license__ = "GPL"
__version__ = "2.0"
__email__ = "carlosesl07@gmail.com"
__maintainer__ = "Carlos Eduardo Sousa Lima"
__status__ = "Production"

'''
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import smapm
from pyswarms.single.global_best import GlobalBestPSO
import pandas as pd
from sklearn.metrics import r2_score, root_mean_squared_error

#%%

def get_FO(x, area, pr, pet, q_obs, warm):
    FO = []
    for params in x:
        q_sim = smapm.smapm(params, area, pr, pet)
        FO.append(-r2_score(q_obs[warm:], q_sim[warm:]))

    return FO
def get_PBIAS(y_true, y_hat):

    if y_true.ndim > 1:
        y_true = y_true.flatten()
    if y_hat.ndim > 1:
        y_hat = y_hat.flatten()
    diff = y_true - y_hat
    PBIAS = np.sum(diff)/np.sum(y_true)

    return (PBIAS*100)

def get_NSE(y_true, y_hat):

    if y_true.ndim > 1:
        y_true = y_true.flatten()
    if y_hat.ndim > 1:
        y_hat = y_hat.flatten()

    NSE = r2_score(y_true, y_hat)

    return NSE

def get_KGE(y_true, y_hat):

    if y_true.ndim > 1:
        y_true = y_true.flatten()
    if y_hat.ndim > 1:
        y_hat = y_hat.flatten()

    R = np.corrcoef(y_true, y_hat)[1,0]

    mean_ratio = np.sum(y_true)/np.sum(y_hat)

    CV_true = np.std(y_true, ddof = 1)/np.mean(y_true)
    CV_hat = np.std(y_hat, ddof = 1)/np.mean(y_hat)

    CV_ratio = CV_hat/CV_true

    KGE = 1 - np.power(
    np.power((R-1),2) + 
    np.power((mean_ratio - 1),2) + 
    np.power((CV_ratio - 1),2), 0.5)

    return KGE

def get_RMSE(y_true, y_hat):

    if y_true.ndim > 1:
        y_true = y_true.flatten()
    if y_hat.ndim > 1:
        y_hat = y_hat.flatten()

    diff_quad = np.power(y_true - y_hat,2)
    
    RMSE = np.power(diff_quad.sum()/len(y_true), 0.5)

    return RMSE

def get_corrcoef(y_true, y_hat):

    if y_true.ndim > 1:
        y_true = y_true.flatten()
    if y_hat.ndim > 1:
        y_hat = y_hat.flatten()

    R = np.corrcoef(y_true, y_hat)[1,0]

    return R

def import_2_csv(df, filename):
    
    df.to_csv(filename, index = True, header = True)
    
    return 


#%%
epq_df = pd.read_excel("input_data.xlsx", sheet_name = "EPQ", index_col = 0)
epq_df.index = pd.to_datetime(epq_df.index)
epq_df = epq_df.dropna(axis = 0, how = "any")

train_df = epq_df.loc[(epq_df.index >= pd.to_datetime("1973-01-01")) &
                (epq_df.index <= pd.to_datetime("2008-12-01"))]

test_df = epq_df.loc[(epq_df.index >= pd.to_datetime("2009-01-01")) &
                (epq_df.index <= pd.to_datetime("2024-03-01"))]

q_train = train_df["Q"].to_numpy().flatten()
pr_train = train_df["P"].to_numpy().flatten()
pet_train = train_df["ETP"].to_numpy().flatten()

q_test = test_df["Q"].to_numpy().flatten()
pr_test = test_df["P"].to_numpy().flatten()
pet_test = test_df["ETP"].to_numpy().flatten()


#%%
warm = 12
drainage_area = 4051.29198

bnd_params = (np.array([400, 0.1, 0, 1, 0, 0]), 
              np.array([5000, 10, 70, 6, 100, 100]))

options = {'c1': 1.5, 'c2': 1.5, 'w': 0.9}
optimizer = GlobalBestPSO(n_particles=50, dimensions=6 , options=options, bounds=bnd_params)

cost, pos = optimizer.optimize(get_FO, iters = 250,
            area = drainage_area, 
            pr = pr_train, pet = pet_train, q_obs = q_train, warm = warm)

import_2_csv(df = pd.DataFrame(pos,
            index = ["sat", "pes", "crec", "k", "tuin", "ebin"]),
            filename = "outputs/opt_coef.csv")
#%%
q_sim_train = smapm.smapm(pos, area = drainage_area,
                   prec = pr_train,
                   pet = pet_train)

q_sim_test = smapm.smapm(pos, area = drainage_area,
                   prec = pr_test,
                   pet = pet_test)
metrics_df = pd.DataFrame(
    [
        [
            get_corrcoef(q_train[warm:], q_sim_train[warm:]),
            get_corrcoef(q_test[warm:], q_sim_test[warm:])],
        [
            get_RMSE(q_train[warm:], q_sim_train[warm:]),
            get_RMSE(q_test[warm:], q_sim_test[warm:])
        ],
        [   
            get_PBIAS(q_train[warm:], q_sim_train[warm:]),
            get_PBIAS(q_test[warm:], q_sim_test[warm:])
        ],
        [
            get_NSE(q_train[warm:], q_sim_train[warm:]),
            get_NSE(q_test[warm:], q_sim_test[warm:]),
        ],
        [
            get_KGE(q_train[warm:], q_sim_train[warm:]),
            get_KGE(q_test[warm:], q_sim_test[warm:])
        ]
    ], 
    index = ["corr", "RMSE", "PBIAS", "NSE", "KGE"],
    columns = ["train", "test"]
)
metrics_df.to_csv("outputs/opt_metrics.csv", index = True, header = True)


train_out = pd.DataFrame({"obs": q_train[warm:], "sim": q_sim_train[warm:]},
                         index = train_df.index[warm:])
train_out.to_csv("outputs/q_sim_train.csv", index = True, header = True)
test_out = pd.DataFrame({"obs": q_test[warm:], "sim": q_sim_test[warm:]},
                         index = test_df.index[warm:])
test_out.to_csv("outputs/q_sim_test.csv", index = True, header = True)
#%%


#%%