"""
Copyright (c) 2018 Intel Corporation.
Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:
The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
"""
   This script is used to train the GMM model on dataset Testset1 & Testset2
    Testset1(1st_test):
        bearing 7(bearing 4, y axis), Fail case
        bearing 2(bearing 2, x axis), Pass case
    Testset2(2nd_test):
        bearing 0(bearing 1 ), Fail case
        bearing 1(bearing 2), Pass case
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.mixture import GaussianMixture
import sys
sys.path.insert(0, '../')
from utils import cal_max_freq,create_dataframe
from influxdb import DataFrameClient
import json
import os

testset1_dbname = "1st_test"
testset2_dbname = "2nd_test"

# Connecting to influx for loading 1st_test
testset1_influxdb_client = DataFrameClient("localhost", "8086", "admin","admin",testset1_dbname)    
testset1_freq_comp1, testset1_freq_comp2, testset1_freq_comp3, testset1_freq_comp4, testset1_freq_comp5 = (pd.DataFrame() for _ in range(5))
testset1_query = testset1_influxdb_client.query("select * from freq_comp")
testset1_temporary_df = testset1_query['freq_comp']
testset1_freq_dataframes = ['testset1_freq_comp1', 'testset1_freq_comp2', 
                   'testset1_freq_comp3', 'testset1_freq_comp4', 
                   'testset1_freq_comp5']
testset1_length = int(len(testset1_temporary_df)/5)
for i , c in enumerate (testset1_freq_dataframes, 0):
    exec('{} = testset1_temporary_df.iloc[i*testset1_length:i*testset1_length+testset1_length, : ]'.format(c,i))

# Connecting to influx for loading 2nd_test
testset2_influxdb_client = DataFrameClient("localhost", "8086", "admin","admin",testset2_dbname)
testset2_freq_comp1, testset2_freq_comp2, testset2_freq_comp3, testset2_freq_comp4, testset2_freq_comp5 = (pd.DataFrame() for _ in range(5))
testset2_query = testset2_influxdb_client.query("select * from freq_comp")
testset2_temporary_df = testset2_query['freq_comp']
testset2_freq_dataframes = ['testset2_freq_comp1', 'testset2_freq_comp2', 
                   'testset2_freq_comp3', 'testset2_freq_comp4', 
                   'testset2_freq_comp5']
testset2_length = int(len(testset2_temporary_df)/5)
for i , c in enumerate (testset2_freq_dataframes, 0):
    exec('{} = testset2_temporary_df.iloc[i*testset2_length:i*testset2_length+testset2_length, : ]'.format(c,i))

# Create data frame of the failed bearing from testset1 & testset2
result1 = create_dataframe(testset1_freq_comp1, testset1_freq_comp2, testset1_freq_comp3, testset1_freq_comp4, testset1_freq_comp5, 7)
result2 = create_dataframe(testset2_freq_comp1, testset2_freq_comp2, testset2_freq_comp3, testset2_freq_comp4, testset2_freq_comp5, 0)

# Create data frame of the passed bearing from testset1 & testset2
result3 = create_dataframe(testset1_freq_comp1, testset1_freq_comp2, testset1_freq_comp3, testset1_freq_comp4, testset1_freq_comp5, 2)
result3 = result3[:1800]

result4 = create_dataframe(testset2_freq_comp1, testset2_freq_comp2, testset2_freq_comp3, testset2_freq_comp4, testset2_freq_comp5, 1)
result4 = result4[:800]

frames = [result1,result2,result3,result4]
result = pd.concat(frames)

X = result[["fmax1","fmax2","fmax3","fmax4","fmax5"]]

# Training the GMM algorithm 
gmm  =  GaussianMixture(n_components = 3,max_iter = 500,covariance_type = 'full',n_init = 1,random_state = 42).fit(X)
labels = gmm.predict(X)

# Save the model
filename = "GMM_all.npy"
np.save(filename,gmm)

# Saving the training bearings
testset1_train_bearings = [7,2]
testset2_tain_bearings = [0,1]
data = {}  
data['training_bearings'] = []  
data['training_bearings'].append({  
    '1st_test': testset1_train_bearings,
    '2nd_test': testset2_tain_bearings,
})

with open('config.txt', 'w') as outfile:  
    json.dump(data, outfile)

