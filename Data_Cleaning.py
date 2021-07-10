## Code for MVDC Project to retrieve and clean met station data from airport (temperature)
## Data is from: https://mesonet.agron.iastate.edu/request/download.phtml?network=AK_ASOS
## MJC Summer 2021


import scipy.io as spio
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
from datetime import datetime, timedelta
import dateutil as dt
from matplotlib.dates import DateFormatter
import datetime

os.chdir('C:/users/michelechamberlin/Desktop/ACEP Projects/MVDC Mentoring/Data/Met Data')

####################################################################################################################################################################################################################################
# This code takes a dataset with nan values and fills the nans of the desired year (2018) with values from the previous
# and the next year and then ultimately simply replaces the remaining nans with bfill
####################################################################################################################################################################################################################################

# Import Data
# region
data = pd.DataFrame()
data = pd.read_csv('PAGH.csv', parse_dates=['valid'], index_col='valid')
# clean data
data = data[data['tmpc'] != 'M']
# plt.plot(data['tmpf'])
TempC = data['tmpc'].astype(float)
TempC = TempC.resample('h').mean()
TempC_old = TempC.copy()  # for comparison
TempC.to_csv('TempC_PAGH.csv')
# plt.close('all')
# plt.plot(TempC.isna())


############################# Trial Code to identify length of consecutively missing data
TempC = TempC.to_frame()
TempC['NAN'] = TempC.isna().astype(int)
# Loop to write the number of consecutive nans in the NAN column of each of the values involved
for i in range(len(TempC)):
    if TempC['NAN'][i] > 0 and TempC['NAN'][i - 1] == 0:
        print('i ' + str(i))
        j = i
        count_nan = 0
        while TempC['NAN'][j] > 0:
            count_nan = count_nan + 1
            j = j + 1
            # print('while')
        TempC['NAN'][i] = count_nan
        print('count ' + str(count_nan))
    elif TempC['NAN'][i] > 0:
        TempC['NAN'][i] = TempC['NAN'][i - 1]


#Check new column
plt.plot(TempC['NAN'])

# Assuming a daily cycle, replace data holes shorter than one day with average of surrounding values
# filter nan shorter or equal to 1 day, 24 hours
Short_Missing = TempC[TempC['NAN']<23]
Short_Missing = Short_Missing[Short_Missing['NAN']>0]
plt.close('all')
plt.plot(TempC[TempC['NAN']<23])
plt.plot(Short_Missing)

for i in range(len(Short_Missing)):
    # print(TempC[TempC.index==Short_Missing.index[i]]['tmpc'] )
    previous_day = TempC[TempC.index == (Short_Missing.index[i] - pd.Timedelta(days=1))]['tmpc'].values
    next_day = TempC[TempC.index == (Short_Missing.index[i] + pd.Timedelta(days=1))]['tmpc'].values
    a = [previous_day[0], next_day[0]]
    TempC.loc[TempC.index == Short_Missing.index[i]] = np.nanmean(a)
    # print(TempC[TempC.index==Short_Missing.index[i]]['tmpc'] )


##Trial to get gradient of missing data and use as calibration for the data to be filled in the gap

for i in range(len(Short_Missing)):
    if TempC[TempC.index == Short_Missing.index[i]]['tmpc'].isna()[0]: #Condition is set because the following code fills mutliple consecutive na values
        #identify indices immediately before and after nan spot
        TempC_index = TempC[TempC.index == Short_Missing.index[i]].index
        datapoint_before_nan = TempC[TempC.index == (Short_Missing.index[i] - pd.Timedelta(days=1/24))]['tmpc']#.values
        index_before_nan=datapoint_before_nan.index[0]
        while TempC[TempC.index == TempC_index[0]].isna()['tmpc'][0]:
            TempC_index= TempC_index+pd.Timedelta(days=1 / 24)
        datapoint_after_nan = TempC[TempC.index == (TempC_index[0])]['tmpc']
        index_after_nan = datapoint_after_nan.index[0]
        #identify gradient Nans
        Number_of_NANs= TempC[TempC.index == Short_Missing.index[i]]['NAN'][0]
        Delta_Y=(datapoint_after_nan.values-datapoint_before_nan.values)[0]
        Gradient = Delta_Y/Number_of_NANs
        #identify Gradient day before
        #Number_of_NANs = TempC[TempC.index == Short_Missing.index[i]-- pd.Timedelta(days=1)]['NAN'][0]
        Delta_Y = (TempC[TempC.index == index_after_nan-pd.Timedelta(days=1)]['tmpc'][0] - TempC[TempC.index == index_before_nan-pd.Timedelta(days=1)]['tmpc'][0])
        Gradient_before = Delta_Y / Number_of_NANs
        # identify Gradient day after
        Delta_Y = (TempC[TempC.index == index_after_nan + pd.Timedelta(days=1)]['tmpc'][0] -
                   TempC[TempC.index == index_before_nan + pd.Timedelta(days=1)]['tmpc'][0])
        Gradient_after = Delta_Y / Number_of_NANs
        for j in range(Number_of_NANs):
            print(j)



TempC['NAN'].hist(bins=100)
a = 6820
TempC[Short_Missing.index[i],]

TempC[a:a + 50]

# First Round
print('Nan values are ' + str(TempC.isna().sum()) + ' or ' + str(
    np.round(100 * TempC.isna().sum() / len(TempC), 2)) + '%')
print('Nan values in 2018 are ' + str(TempC['2018'].isna().sum()) + ' or ' + str(
    np.round(100 * TempC['2018'].isna().sum() / len(TempC['2018']), 2)) + '%')
index = TempC.index[TempC.apply(np.isnan)]
index_bad = index[index.year == 2018]
index_good = index_bad - pd.Timedelta(days=365)
TempC[TempC.index.isin(index_bad)] = TempC[TempC.index.isin(index_good)].values
# Second Round
print('Nan values are ' + str(TempC.isna().sum()) + ' or ' + str(
    np.round(100 * TempC.isna().sum() / len(TempC), 2)) + '%')
print('Nan values in 2018 are ' + str(TempC['2018'].isna().sum()) + ' or ' + str(
    np.round(100 * TempC['2018'].isna().sum() / len(TempC['2018']), 2)) + '%')
index = TempC.index[TempC.apply(np.isnan)]
index_bad = index[index.year == 2018]
index_good = index_bad + pd.Timedelta(days=365)
TempC[TempC.index.isin(index_bad)] = TempC[TempC.index.isin(index_good)].values
print('Nan values are ' + str(TempC.isna().sum()) + ' or ' + str(
    np.round(100 * TempC.isna().sum() / len(TempC), 2)) + '%')
print('Nan values in 2018 are ' + str(TempC['2018'].isna().sum()) + ' or ' + str(
    np.round(100 * TempC['2018'].isna().sum() / len(TempC['2018']), 2)) + '%')

# Last Round
TempC[TempC.index.year == 2018] = TempC[TempC.index.year == 2018].fillna(method='bfill')
print('Nan values are ' + str(TempC.isna().sum()) + ' or ' + str(
    np.round(100 * TempC.isna().sum() / len(TempC), 2)) + '%')
print('Nan values in 2018 are ' + str(TempC['2018'].isna().sum()) + ' or ' + str(
    np.round(100 * TempC['2018'].isna().sum() / len(TempC['2018']), 2)) + '%')

# Now plot 'clean dataset'

TempC_final = TempC['tmpc']

plt.close('all')
plt.plot(TempC_final, label='new')
# comparison
plt.plot(TempC_old, label='old')
plt.legend()

# create fake timeindex to have datetime index, YEAR is not relevant (remove from plots)
beginning = datetime(2018, 1, 1)
date_today = datetime.now()
days = pd.date_range(beginning, beginning + timedelta(365), freq='1h')
date_ind = days[days.year == 2018]
data.index = date_ind

data.columns  # 'excess_wind', 'ESS_SOC', 'unmet_load', 'wind_power', 'load_WTP'
# Change Date format to only show month name in plot
formatter = DateFormatter('%b')  # ('%Y-%m-%d %H:%M:%S')

plt.plot(data['load_WTP'], label='Load [kW]')
plt.plot(data['wind_power'], label='Wind Generation [kW]')
plt.plot(data['excess_wind'], label='Excess Wind Generation [kW]')
plt.legend()
# plt.gcf().axes[0].xaxis.set_major_formatter(formatter)

# endregion
