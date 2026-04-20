#%%
__author__ = "Carlos Eduardo Sousa Lima"
__license__ = "GPL"
__version__ = "2.0"
__email__ = "carlosesl07@gmail.com"
__maintainer__ = "Carlos Eduardo Sousa Lima"
__status__ = "Production"

import cdsapi
import time
import os 
def create_except_file():

    open("get_data_except_log.txt", "w").close()
    open("list_download_models.txt", 'w').close()
    return

def create_folder(model):
    if not os.path.exists("{}".format(model)):
        os.makedirs(model)
#%%

create_except_file()
start = time.perf_counter()
client = cdsapi.Client()

dataset = "projections-cmip6"

extents = [-5.93, #Norte
        -49.460, #Oeste
        -8.43, #Sul
        -46.960] #Leste

years_hist = list(range(1850, 2014 + 1, 1))
years_hist = ['{}'.format(x) for x in years_hist]
years_proj = list(range(2015, 2099 + 1, 1))
years_proj = ['{}'.format(x) for x in years_proj]


# experiments = ['ssp5_8_5', 'ssp2_4_5','ssp3_7_0','ssp1_2_6', 'historical']
experiments = ['ssp5_8_5', 'ssp2_4_5','historical']

variables = ['precipitation']
            #  'daily_maximum_near_surface_air_temperature',
            #  'daily_minimum_near_surface_air_temperature']
#All Models
# models = [  
#     'access_cm2', 'awi_cm_1_1_mr', 'bcc_csm2_mr', 'cams_csm1_0', 'canesm5_canoe',
#     'cesm2_fv2', 'cesm2_waccm_fv2', 'cmcc_cm2_hr4', 'cmcc_esm2', 'cnrm_cm6_1_hr',
#     'e3sm_1_0', 'e3sm_1_1_eca', 'ec_earth3_aerchem', 'fgoals_f3_l', 'fio_esm_2_0',
#     'hadgem3_gc31_ll', 'iitm_esm', 'inm_cm5_0', 'ipsl_cm6a_lr', 'miroc6',
#     'miroc_es2l', 'mpi_esm1_2_hr', 'mri_esm2_0', 'norcpm1', 'noresm2_mm',
#     'taiesm1', 'access_esm1_5', 'awi_esm_1_1_lr', 'bcc_esm1', 'canesm5',
#     'cesm2', 'cesm2_waccm', 'cmcc_cm2_sr5', 'cnrm_cm6_1', 'cnrm_esm2_1',
#     'e3sm_1_1', 'ec_earth3_cc', 'ec_earth3_veg_lr', 'fgoals_g3', 'gfdl_esm4',
#     'giss_e2_1_h', 'hadgem3_gc31_mm', 'inm_cm4_8', 'ipsl_cm5a2_inca', 'kace_1_0_g',
#     'mcm_ua_1_0', 'miroc_es2h', 'mpi_esm1_2_lr', 'nesm3', 'sam0_unicon',
#     'ukesm1_0_ll']

#Models with daily precipitation Data
models = [
    'access_cm2',
    # 'awi_cm_1_1_mr', #Sem historical
    'bcc_csm2_mr',
    # 'cams_csm1_0',  
    'canesm5',
    'cesm2',
    'cmcc_cm2_sr5',
    "cmcc_esm2",
    'cnrm_cm6_1',
    'cnrm_esm2_1',
    'ec_earth3_cc',
    'ec_earth3_veg_lr',
    'fgoals_g3',
    'gfdl_esm4',
    'hadgem3_gc31_ll',
    'iitm_esm',
    'inm_cm4_8',
    'inm_cm5_0',
    'ipsl_cm6a_lr',
    'kace_1_0_g',
    'miroc6',
    'miroc_es2l',
    'mpi_esm1_2_lr',
    'mri_esm2h_0',
    'nesm3',
    'noresm2_mm',
    'ukesm10_0_ll'
    ]

#%%
for model in models:
    print(model)
    for experiment in experiments:
        if experiment == 'historical':
            years_list = years_hist
        else:
            years_list = years_proj
        for var in variables:
            try:
                request = {
                    "temporal_resolution": "daily",
                    "experiment": experiment,
                    "variable": var,
                    "model": model,
                    "year": years_list,
                    "month": [
                        "01", "02", "03",
                        "04", "05", "06",
                        "07", "08", "09",
                        "10", "11", "12"
                    ],
                    "day": [
                        "01", "02", "03",
                        "04", "05", "06",
                        "07", "08", "09",
                        "10", "11", "12",
                        "13", "14", "15",
                        "16", "17", "18",
                        "19", "20", "21",
                        "22", "23", "24",
                        "25", "26", "27",
                        "28", "29", "30",
                        "31"
                    ],
                    "area": extents
                }
                client.retrieve(dataset, request).download()

            except:
                with open('get_data_except_log.txt', mode = "a") as file:
                    file.write('Failed to get data: Model {} - Experiment {} - Variable {} \n'.format(model, experiment, var))

    with open('list_download_models.txt', mode = "a") as file:
        file.write("{} Baixado\n".format(model))
end = time.perf_counter()
print("\n\n##### Tempo de Simulação {:.3f} segundos #####".format(end-start))
            
#%%
