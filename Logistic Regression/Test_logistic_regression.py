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

import numpy as np
import pandas as pd
import json
import os 
import sys
from influxdb import InfluxDBClient
from influxdb import DataFrameClient
sys.path.insert(0, '../')
from utils import create_dataframe

# Connecting to influxDb
influxdb1_client = InfluxDBClient("localhost", "8086", "admin","admin","Predictions_testset1")
influxdb1_client.create_database("Predictions_testset1")
influxdb2_client = InfluxDBClient("localhost", "8086", "admin","admin","Predictions_testset2")
influxdb2_client.create_database("Predictions_testset2")

dbname = input("Enter the database name: ")
if(dbname == '1st_test' or dbname == '2nd_test'):
    if (dbname=="1st_test"):
        no_of_bearings = 8
        influxdb_client = DataFrameClient("localhost", "8086", "admin","admin",dbname)
                
    elif(dbname=="2nd_test"):
        no_of_bearings = 4
        influxdb_client = DataFrameClient("localhost", "8086", "admin","admin",dbname)
    
    frequency_component1, frequency_component2, frequency_component3, frequency_component4, frequency_component5 = (pd.DataFrame() for _ in range(5))
    query = influxdb_client.query("select * from freq_comp")
    temporary_df = query['freq_comp']
    
    freq_dataframes = ['frequency_component1', 'frequency_component2', 
                       'frequency_component3', 'frequency_component4', 
                       'frequency_component5']
    testset_length = int(len(temporary_df)/5)
    for i , c in enumerate (freq_dataframes, 0):
        exec('{} = temporary_df.iloc[i*testset_length:i*testset_length+testset_length, : ]'.format(c,i))
    
    # Loading the test bearings
    with open('config.txt') as json_file:  
        data = json.load(json_file)
        for p in data['training_bearings']:
            if(no_of_bearings == 8):
                training_bearings = list(p['1st_test'])
            if(no_of_bearings == 4):
                training_bearings = list(p['2nd_test'])
                
    bearing_list = []
    for i in range(no_of_bearings):
        bearing_list.append(i)
        
    testing_bearings = list(np.setdiff1d(bearing_list,training_bearings))
    
    # Load the model
    filename = "logisticRegressionModel.npy"
    logistic_regr = np.load(filename).item()
    
    print("Testing ", dbname, "...")
    prediction_last_100 = []
    
    for k in testing_bearings:
        print("\nTesting bearing ",k+1)
        x = create_dataframe(frequency_component1, frequency_component2,
                             frequency_component3, frequency_component4,
                             frequency_component5,k)
        
        predictions  =  logistic_regr.predict(x)
        
        prediction_last_100.append(predictions[-100:])
        # Count no. of labels which are failed
        check_one = list(predictions[-100:]).count(1)
        
        json_body = [
            {
                "measurement": "LR",
                "tags": {
                    "type": "B"+str(k+1),
                },
                "fields": {
                    "label": check_one,
                }
            }
            ]
        if (no_of_bearings == 8):
            influxdb1_client.write_points(json_body)
        elif (no_of_bearings == 4):
            influxdb2_client.write_points(json_body)
    
        # Count no. of labels which are passed
        check_zero = list(predictions[-100:]).count(0)
    
        if(check_one >= 35):
            print("Bearing " + str(k+1) +" is suspected to fail!")
        else:
            print("Bearing " + str(k+1) + " is working normally.")

else:
    print("Invalid Database name")
    exit()
