import pandas as pd
from datetime import datetime, timedelta
import numpy as np

beginning = datetime(2018, 1, 1)
days = pd.date_range(beginning, beginning + timedelta(365-1/24/4), freq='15Min')


for i in ['Ambler', 'Shungnak']:
    print(i)
    #Import dataset
    load=pd.read_csv('C:/users/michelechamberlin/Desktop/ACEP Projects/MVDC Mentoring/Data/Load Data/'+str(i)+'_alone_2018_kW_corrected.csv', header=None)
    load.index = days
    #Resample data to one hour resolution
    load_1h = load.resample('1h').mean()
    load_1h.to_csv('C:/users/michelechamberlin/Desktop/ACEP Projects/MVDC Mentoring/Data/Load Data/'+str(i)+'_alone_2018_kW_corrected_1h.csv', index=None, header=None)
    print(np.sum(load_1h))


